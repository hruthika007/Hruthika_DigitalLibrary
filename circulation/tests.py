import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Author, Book, Member, CirculationRecord, DAILY_FINE_RATE


class CirculationBusinessLogicTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(
            name="Robert C. Martin",
            biography="Uncle Bob software craftsmanship pioneer."
        )
        self.book_available = Book.objects.create(
            title="Clean Code",
            author=self.author,
            isbn="978-0132350884",
            genre="Computer Science",
            total_copies=3,
            available_copies=2
        )
        self.book_out_of_stock = Book.objects.create(
            title="Dune",
            author=self.author,
            isbn="978-0441172719",
            genre="Sci-Fi",
            total_copies=2,
            available_copies=0
        )
        self.member = Member.objects.create(
            name="Sarah Connor",
            member_id="MEM-1001",
            email="sarah@example.com",
            phone="+1 555-0199"
        )

    def test_default_due_date_to_14_days_after_issue(self):
        """Test business logic: Default due date is 14 days after issue"""
        today = timezone.now().date()
        record = CirculationRecord.objects.create(
            book=self.book_available,
            member=self.member,
            issue_date=today
        )
        self.assertEqual(record.due_date, today + datetime.timedelta(days=14))

    def test_reduce_available_copies_when_issued(self):
        """Test business logic: Reduce available copies when a book is issued"""
        initial_available = self.book_available.available_copies
        response = self.client.post(reverse('issue_book'), {
            'book': self.book_available.id,
            'member': self.member.id,
            'issue_date': timezone.now().date().isoformat(),
            'due_date': (timezone.now().date() + datetime.timedelta(days=14)).isoformat(),
            'notes': 'Test issue'
        })
        self.assertEqual(response.status_code, 302)
        self.book_available.refresh_from_db()
        self.assertEqual(self.book_available.available_copies, initial_available - 1)

    def test_do_not_issue_when_available_copies_zero(self):
        """Test business logic: Do not issue a book when available copies are zero"""
        response = self.client.post(reverse('issue_book'), {
            'book': self.book_out_of_stock.id,
            'member': self.member.id,
            'issue_date': timezone.now().date().isoformat(),
            'due_date': (timezone.now().date() + datetime.timedelta(days=14)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)  # Re-rendered with form error
        self.book_out_of_stock.refresh_from_db()
        self.assertEqual(self.book_out_of_stock.available_copies, 0)
        # Verify no circulation record created
        self.assertEqual(CirculationRecord.objects.filter(book=self.book_out_of_stock).count(), 0)

    def test_return_book_increases_copies_and_calculates_fine_if_overdue(self):
        """Test business logic: Increase available copies and calculate overdue fine upon return"""
        today = timezone.now().date()
        issue_date = today - datetime.timedelta(days=20)
        due_date = issue_date + datetime.timedelta(days=14)  # Due 6 days ago!

        record = CirculationRecord.objects.create(
            book=self.book_available,
            member=self.member,
            issue_date=issue_date,
            due_date=due_date,
            returned=False
        )

        initial_available = self.book_available.available_copies
        return_date = today  # 6 days late

        response = self.client.post(reverse('return_book', args=[record.id]), {
            'return_date': return_date.isoformat(),
            'notes': 'Returned late'
        })
        self.assertEqual(response.status_code, 302)

        record.refresh_from_db()
        self.assertTrue(record.returned)
        self.assertEqual(record.return_date, return_date)
        # 6 days late * $1.00 = $6.00
        expected_fine = Decimal('6.00') * DAILY_FINE_RATE
        self.assertEqual(record.fine_amount, expected_fine)

        self.book_available.refresh_from_db()
        self.assertEqual(self.book_available.available_copies, initial_available + 1)

    def test_return_on_time_has_zero_fine(self):
        """Test returning a book on or before due date incurs $0.00 fine"""
        today = timezone.now().date()
        issue_date = today - datetime.timedelta(days=5)
        due_date = issue_date + datetime.timedelta(days=14)

        record = CirculationRecord.objects.create(
            book=self.book_available,
            member=self.member,
            issue_date=issue_date,
            due_date=due_date,
            returned=False
        )

        response = self.client.post(reverse('return_book', args=[record.id]), {
            'return_date': today.isoformat(),
            'notes': 'Returned early'
        })
        self.assertEqual(response.status_code, 302)

        record.refresh_from_db()
        self.assertTrue(record.returned)
        self.assertEqual(record.fine_amount, Decimal('0.00'))

    def test_catalog_view(self):
        response = self.client.get(reverse('book_catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean Code")
        self.assertContains(response, "Dune")

    def test_member_dashboard_view(self):
        response = self.client.get(reverse('member_detail', args=[self.member.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.name)
        self.assertContains(response, self.member.member_id)

    def test_api_fine_calculator(self):
        due = "2026-10-01"
        ret = "2026-10-06"  # 5 days late
        response = self.client.get(reverse('api_calculate_fine'), {
            'due_date': due,
            'return_date': ret,
            'rate': '1.00'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_overdue'])
        self.assertEqual(data['days_overdue'], 5)
        self.assertEqual(data['fine_amount'], 5.0)
