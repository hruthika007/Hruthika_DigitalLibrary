import datetime
from django import forms
from django.utils import timezone
from .models import Book, Member, CirculationRecord, Author, DAILY_FINE_RATE


class BookIssueForm(forms.ModelForm):
    class Meta:
        model = CirculationRecord
        fields = ['book', 'member', 'issue_date', 'due_date', 'notes']
        widgets = {
            'book': forms.Select(attrs={
                'class': 'form-select select2-book',
                'id': 'issue-book-select'
            }),
            'member': forms.Select(attrs={
                'class': 'form-select select2-member',
                'id': 'issue-member-select'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'issue-date-input'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'due-date-input'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional issue notes or condition memo'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()
        self.fields['issue_date'].initial = today
        self.fields['due_date'].initial = today + datetime.timedelta(days=14)
        
        # Order and format choices
        self.fields['book'].queryset = Book.objects.select_related('author').all()
        self.fields['member'].queryset = Member.objects.all().order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        issue_date = cleaned_data.get('issue_date')
        due_date = cleaned_data.get('due_date')

        if book:
            if book.available_copies <= 0:
                self.add_error('book', f"'{book.title}' is currently out of stock. Available copies: 0.")

        if issue_date and due_date:
            if due_date < issue_date:
                self.add_error('due_date', "Due date cannot be earlier than the issue date.")

        return cleaned_data


class BookReturnForm(forms.Form):
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'return-date-input'}),
        initial=timezone.now().date
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional condition report or fee notes'})
    )

    def clean_return_date(self):
        return_date = self.cleaned_data.get('return_date')
        return return_date


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies', 'cover_url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book Title'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN-10 or ISBN-13'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cover_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://images.unsplash.com/...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief synopsis...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_copies')
        avail = cleaned_data.get('available_copies')
        if total is not None and avail is not None and avail > total:
            self.add_error('available_copies', 'Available copies cannot be greater than total inventory.')
        return cleaned_data


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'member_id', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'member_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MEM-1050'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'member@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author Full Name'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Author biography...'}),
        }
