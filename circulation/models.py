import datetime
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

DAILY_FINE_RATE = Decimal('1.00')  # $1.00 per day overdue


class Author(models.Model):
    name = models.CharField(max_length=200, help_text="Full name of the author")
    biography = models.TextField(blank=True, default="", help_text="Brief author biography")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.books.count()


class Book(models.Model):
    GENRE_CHOICES = [
        ('Computer Science', 'Computer Science & Tech'),
        ('Fiction', 'Fiction & Literature'),
        ('Sci-Fi', 'Science Fiction & Fantasy'),
        ('Science', 'Science & Mathematics'),
        ('Biography', 'Biography & Memoir'),
        ('History', 'History & Philosophy'),
        ('Business', 'Business & Economics'),
        ('Art', 'Art & Design'),
        ('General', 'General Non-Fiction'),
    ]

    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    isbn = models.CharField(max_length=20, unique=True, help_text="Standard 10 or 13-digit ISBN")
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, default='Fiction')
    total_copies = models.PositiveIntegerField(default=1, help_text="Total inventory count")
    available_copies = models.PositiveIntegerField(default=1, help_text="Current copies on shelf")
    cover_url = models.URLField(max_length=500, blank=True, default="", help_text="Direct link to book cover image")
    description = models.TextField(blank=True, default="", help_text="Plot summary or book overview")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author.name}"

    def clean(self):
        if self.available_copies > self.total_copies:
            raise ValidationError({'available_copies': 'Available copies cannot exceed total copies.'})

    @property
    def is_available(self):
        return self.available_copies > 0

    @property
    def availability_badge_class(self):
        if self.available_copies == 0:
            return "bg-danger"
        elif self.available_copies <= 2:
            return "bg-warning text-dark"
        return "bg-success"

    @property
    def availability_status_text(self):
        if self.available_copies == 0:
            return "Out of Stock"
        elif self.available_copies == 1:
            return "1 copy available"
        return f"{self.available_copies} of {self.total_copies} available"


class Member(models.Model):
    name = models.CharField(max_length=200)
    member_id = models.CharField(max_length=50, unique=True, help_text="Unique Member ID (e.g., MEM-1001)")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30)
    joined_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.member_id})"

    @property
    def active_borrowed_count(self):
        return self.circulations.filter(returned=False).count()

    @property
    def total_borrowed_count(self):
        return self.circulations.count()

    @property
    def overdue_borrowed_count(self):
        today = timezone.now().date()
        return self.circulations.filter(returned=False, due_date__lt=today).count()

    @property
    def total_fines_accumulated(self):
        records = self.circulations.all()
        total = Decimal('0.00')
        today = timezone.now().date()
        for r in records:
            if r.returned:
                total += r.fine_amount
            elif r.due_date < today:
                days = (today - r.due_date).days
                total += Decimal(days) * DAILY_FINE_RATE
        return total


class CirculationRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='circulations')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='circulations')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(help_text="Expected return date (default +14 days from issue)")
    return_date = models.DateField(null=True, blank=True, help_text="Actual return date")
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), help_text="Overdue fine")
    returned = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        status = "Returned" if self.returned else "Active"
        return f"{self.book.title} -> {self.member.name} [{status}]"

    def save(self, *args, **kwargs):
        # Default the due date to 14 days after issue if not explicitly set
        if not self.due_date and self.issue_date:
            self.due_date = self.issue_date + datetime.timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.returned:
            return bool(self.return_date and self.return_date > self.due_date)
        return timezone.now().date() > self.due_date

    @property
    def days_overdue(self):
        if self.returned:
            ref_date = self.return_date or self.due_date
        else:
            ref_date = timezone.now().date()

        if ref_date > self.due_date:
            return (ref_date - self.due_date).days
        return 0

    @property
    def current_estimated_fine(self):
        if self.returned:
            return self.fine_amount
        days = self.days_overdue
        return Decimal(days) * DAILY_FINE_RATE

    @property
    def days_remaining(self):
        if self.returned:
            return 0
        today = timezone.now().date()
        diff = (self.due_date - today).days
        return diff
