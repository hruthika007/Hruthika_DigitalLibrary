from django.contrib import admin
from .models import Author, Book, Member, CirculationRecord


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'book_count')
    search_fields = ('name', 'biography')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies', 'availability_status')
    list_filter = ('genre', 'total_copies')
    search_fields = ('title', 'isbn', 'author__name')
    readonly_fields = ('created_at',)

    @admin.display(description="Availability")
    def availability_status(self, obj):
        return obj.availability_status_text


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_id', 'email', 'phone', 'joined_date', 'active_loans', 'fines')
    search_fields = ('name', 'member_id', 'email', 'phone')
    list_filter = ('joined_date',)

    @admin.display(description="Active Loans")
    def active_loans(self, obj):
        return obj.active_borrowed_count

    @admin.display(description="Fines Accrued")
    def fines(self, obj):
        return f"${obj.total_fines_accumulated:.2f}"


@admin.register(CirculationRecord)
class CirculationRecordAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'issue_date', 'due_date', 'return_date', 'fine_amount', 'returned', 'overdue_status')
    list_filter = ('returned', 'issue_date', 'due_date')
    search_fields = ('book__title', 'member__name', 'member__member_id')
    readonly_fields = ('created_at',)

    @admin.display(description="Overdue Status")
    def overdue_status(self, obj):
        if obj.returned:
            return "Returned"
        if obj.is_overdue:
            return f"Overdue ({obj.days_overdue} days)"
        return "On Schedule"
