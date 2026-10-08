import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from .models import Book, Author, Member, CirculationRecord, DAILY_FINE_RATE
from .forms import BookIssueForm, BookReturnForm, BookForm, MemberForm, AuthorForm


def book_catalog(request):
    """
    Catalog view displaying all books with filter pills, search, and inventory statistics.
    Both server-side filtering and real-time JS instant search are supported.
    """
    query = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    status = request.GET.get('status', '').strip()

    books = Book.objects.select_related('author').all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(isbn__icontains=query) |
            Q(genre__icontains=query)
        )

    if genre and genre != 'All':
        books = books.filter(genre__iexact=genre)

    if status == 'available':
        books = books.filter(available_copies__gt=0)
    elif status == 'out_of_stock':
        books = books.filter(available_copies=0)

    # Portal high-level stats
    total_titles = Book.objects.count()
    all_books_agg = Book.objects.aggregate(
        total_copies=Sum('total_copies'),
        available_copies=Sum('available_copies')
    )
    total_copies = all_books_agg['total_copies'] or 0
    available_copies = all_books_agg['available_copies'] or 0
    issued_copies = max(0, total_copies - available_copies)

    today = timezone.now().date()
    active_loans = CirculationRecord.objects.filter(returned=False).count()
    overdue_loans = CirculationRecord.objects.filter(returned=False, due_date__lt=today).count()
    total_members = Member.objects.count()

    # Distinct genres for filter tabs
    genres = [g[0] for g in Book.GENRE_CHOICES]

    context = {
        'books': books,
        'genres': genres,
        'selected_genre': genre,
        'selected_status': status,
        'search_query': query,
        'stats': {
            'total_titles': total_titles,
            'total_copies': total_copies,
            'available_copies': available_copies,
            'issued_copies': issued_copies,
            'active_loans': active_loans,
            'overdue_loans': overdue_loans,
            'total_members': total_members,
        }
    }
    return render(request, 'circulation/book_catalog.html', context)


def book_detail(request, pk):
    book = get_object_or_404(Book.objects.select_related('author'), pk=pk)
    active_circulations = book.circulations.filter(returned=False).select_related('member')
    past_circulations = book.circulations.filter(returned=True).select_related('member')[:5]

    context = {
        'book': book,
        'active_circulations': active_circulations,
        'past_circulations': past_circulations,
    }
    return render(request, 'circulation/book_detail.html', context)


def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Book '{book.title}' added to the catalog successfully.")
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'circulation/book_form.html', {'form': form, 'title': 'Add New Book'})


def issue_book(request, book_id=None):
    """
    Workflow for issuing a book to a member.
    Enforces business logic:
    - Do not issue if available_copies == 0
    - Reduce available_copies by 1
    - Default due_date = issue_date + 14 days
    """
    initial = {}
    selected_book = None
    if book_id:
        selected_book = get_object_or_404(Book, pk=book_id)
        initial['book'] = selected_book

    member_id = request.GET.get('member_id')
    if member_id:
        initial['member'] = get_object_or_404(Member, pk=member_id)

    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            book = record.book

            # Double-check availability on server side
            if book.available_copies <= 0:
                messages.error(request, f"Cannot issue '{book.title}': No available copies left in stock!")
                return render(request, 'circulation/book_issue.html', {'form': form, 'selected_book': selected_book})

            # Reduce available copies
            book.available_copies -= 1
            book.save()

            # Ensure due_date is set (defaults to +14 days if left empty)
            if not record.due_date:
                record.due_date = record.issue_date + datetime.timedelta(days=14)

            record.returned = False
            record.fine_amount = Decimal('0.00')
            record.save()

            messages.success(
                request,
                f"Successfully issued '{book.title}' to {record.member.name}. "
                f"Due date: {record.due_date.strftime('%b %d, %Y')} (14-day borrowing period)."
            )
            return redirect('member_detail', pk=record.member.pk)
    else:
        form = BookIssueForm(initial=initial)

    return render(request, 'circulation/book_issue.html', {
        'form': form,
        'selected_book': selected_book,
        'fine_rate': DAILY_FINE_RATE
    })


def return_book(request, record_id):
    """
    Workflow for returning an issued book with overdue fine calculation.
    Enforces business logic:
    - Increase available_copies by 1
    - Calculate final overdue fine based on return_date vs due_date
    - Mark record as returned = True
    """
    record = get_object_or_404(CirculationRecord.objects.select_related('book', 'member'), pk=record_id)

    if record.returned:
        messages.info(request, f"This circulation record is already marked as returned on {record.return_date}.")
        return redirect('circulation_list')

    today = timezone.now().date()
    initial_return_date = today

    # Estimate fine for today
    estimated_fine = Decimal('0.00')
    overdue_days = 0
    if today > record.due_date:
        overdue_days = (today - record.due_date).days
        estimated_fine = Decimal(overdue_days) * DAILY_FINE_RATE

    if request.method == 'POST':
        form = BookReturnForm(request.POST)
        if form.is_valid():
            return_date = form.cleaned_data['return_date']
            notes = form.cleaned_data['notes']

            # Calculate overdue fine
            if return_date > record.due_date:
                days_late = (return_date - record.due_date).days
                fine_amount = Decimal(days_late) * DAILY_FINE_RATE
            else:
                fine_amount = Decimal('0.00')
                days_late = 0

            # Update circulation record
            record.returned = True
            record.return_date = return_date
            record.fine_amount = fine_amount
            if notes:
                record.notes = f"{record.notes} | {notes}".strip(" |")
            record.save()

            # Increase book available copies
            book = record.book
            book.available_copies += 1
            book.save()

            if fine_amount > 0:
                messages.warning(
                    request,
                    f"Book '{book.title}' returned. It was overdue by {days_late} days. "
                    f"Overdue fine calculated: ${fine_amount:.2f}."
                )
            else:
                messages.success(
                    request,
                    f"Book '{book.title}' successfully returned on time by {record.member.name}. No overdue fine!"
                )

            return redirect('circulation_list')
    else:
        form = BookReturnForm(initial={'return_date': today})

    context = {
        'record': record,
        'form': form,
        'today': today,
        'overdue_days': overdue_days,
        'estimated_fine': estimated_fine,
        'fine_rate': DAILY_FINE_RATE
    }
    return render(request, 'circulation/book_return.html', context)


def circulation_list(request):
    """
    Circulation records overview with tabs: All, Active, Overdue, Returned.
    """
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    records = CirculationRecord.objects.select_related('book', 'member', 'book__author').all()
    today = timezone.now().date()

    if search_query:
        records = records.filter(
            Q(book__title__icontains=search_query) |
            Q(member__name__icontains=search_query) |
            Q(member__member_id__icontains=search_query) |
            Q(book__isbn__icontains=search_query)
        )

    if status_filter == 'active':
        records = records.filter(returned=False)
    elif status_filter == 'overdue':
        records = records.filter(returned=False, due_date__lt=today)
    elif status_filter == 'returned':
        records = records.filter(returned=True)

    # Metrics
    total_count = CirculationRecord.objects.count()
    active_count = CirculationRecord.objects.filter(returned=False).count()
    overdue_count = CirculationRecord.objects.filter(returned=False, due_date__lt=today).count()
    returned_count = CirculationRecord.objects.filter(returned=True).count()
    total_fines_collected = CirculationRecord.objects.filter(returned=True).aggregate(Sum('fine_amount'))['fine_amount__sum'] or Decimal('0.00')

    context = {
        'records': records,
        'status_filter': status_filter,
        'search_query': search_query,
        'today': today,
        'fine_rate': DAILY_FINE_RATE,
        'metrics': {
            'total': total_count,
            'active': active_count,
            'overdue': overdue_count,
            'returned': returned_count,
            'fines_collected': total_fines_collected,
        }
    }
    return render(request, 'circulation/circulation_list.html', context)


def member_list(request):
    search_query = request.GET.get('q', '').strip()
    members = Member.objects.all()

    if search_query:
        members = members.filter(
            Q(name__icontains=search_query) |
            Q(member_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    context = {
        'members': members,
        'search_query': search_query,
        'total_members': Member.objects.count(),
    }
    return render(request, 'circulation/member_list.html', context)


def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    today = timezone.now().date()

    active_loans = member.circulations.filter(returned=False).select_related('book', 'book__author').order_by('due_date')
    borrowing_history = member.circulations.filter(returned=True).select_related('book', 'book__author').order_by('-return_date')

    # Calculate pending fines
    pending_fines = Decimal('0.00')
    for loan in active_loans:
        if loan.due_date < today:
            days = (today - loan.due_date).days
            pending_fines += Decimal(days) * DAILY_FINE_RATE

    fines_paid = member.circulations.filter(returned=True).aggregate(Sum('fine_amount'))['fine_amount__sum'] or Decimal('0.00')

    context = {
        'member': member,
        'active_loans': active_loans,
        'borrowing_history': borrowing_history,
        'today': today,
        'pending_fines': pending_fines,
        'fines_paid': fines_paid,
        'fine_rate': DAILY_FINE_RATE,
    }
    return render(request, 'circulation/member_detail.html', context)


def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"Member '{member.name}' ({member.member_id}) registered successfully!")
            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm()
    return render(request, 'circulation/member_form.html', {'form': form, 'title': 'Register New Member'})


def author_list(request):
    authors = Author.objects.annotate(num_books=Count('books')).order_by('name')
    return render(request, 'circulation/author_list.html', {'authors': authors})


def author_create(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f"Author '{author.name}' added successfully.")
            return redirect('author_list')
    else:
        form = AuthorForm()
    return render(request, 'circulation/author_form.html', {'form': form, 'title': 'Add Author'})


def due_date_calculator(request):
    """
    Interactive Due-Date and Overdue Fine Calculator page.
    Allows students/users to test and compute issue dates, 14-day default due dates,
    simulated return dates, overdue day counts, and fine breakdowns in real-time.
    """
    today = timezone.now().date()
    default_due = today + datetime.timedelta(days=14)

    context = {
        'today': today.isoformat(),
        'default_due': default_due.isoformat(),
        'fine_rate': float(DAILY_FINE_RATE),
    }
    return render(request, 'circulation/calculator.html', context)


def api_calculate_fine(request):
    """
    JSON API endpoint for real-time fine calculation preview.
    Accepts: ?due_date=YYYY-MM-DD&return_date=YYYY-MM-DD&rate=1.00
    """
    due_str = request.GET.get('due_date')
    return_str = request.GET.get('return_date')
    rate_str = request.GET.get('rate', str(DAILY_FINE_RATE))

    try:
        due_date = datetime.date.fromisoformat(due_str)
        return_date = datetime.date.fromisoformat(return_str) if return_str else timezone.now().date()
        rate = Decimal(rate_str)

        if return_date > due_date:
            days_overdue = (return_date - due_date).days
            fine = round(Decimal(days_overdue) * rate, 2)
            is_overdue = True
        else:
            days_overdue = 0
            fine = Decimal('0.00')
            is_overdue = False

        return JsonResponse({
            'success': True,
            'is_overdue': is_overdue,
            'days_overdue': days_overdue,
            'fine_amount': float(fine),
            'formatted_fine': f"${fine:.2f}",
            'due_date': due_date.isoformat(),
            'return_date': return_date.isoformat(),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
