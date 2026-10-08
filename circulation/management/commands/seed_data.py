import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from circulation.models import Author, Book, Member, CirculationRecord, DAILY_FINE_RATE


class Command(BaseCommand):
    help = "Seed database with rich sample authors, books, members, and circulation records"

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample data for Digital Library Portal...")

        # Clear existing data to avoid duplicates
        CirculationRecord.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()
        Member.objects.all().delete()

        # 1. Authors
        authors_data = [
            {
                "name": "Robert C. Martin",
                "biography": "Known affectionately as 'Uncle Bob', an American software engineer, author, and co-author of the Agile Manifesto."
            },
            {
                "name": "Frank Herbert",
                "biography": "American science-fiction author best known for the 1965 novel Dune and its five sequels in the Dune universe."
            },
            {
                "name": "Yuval Noah Harari",
                "biography": "Israeli public intellectual, historian and professor in the Department of History at the Hebrew University of Jerusalem."
            },
            {
                "name": "Martin Fowler",
                "biography": "British software engineer, author and international speaker on software development, specialising in object-oriented analysis and refactoring."
            },
            {
                "name": "George Orwell",
                "biography": "English novelist, essayist, journalist, and critic whose work is marked by lucid prose and opposition to totalitarianism."
            },
            {
                "name": "Walter Isaacson",
                "biography": "American author, journalist, and professor known for bestselling biographies of Steve Jobs, Albert Einstein, and Leonardo da Vinci."
            },
            {
                "name": "Carl Sagan",
                "biography": "American astronomer, planetary scientist, and science communicator known for Cosmos and his pioneering research on extraterrestrial life."
            },
            {
                "name": "J.K. Rowling",
                "biography": "British author and philanthropist best known for writing the seven-book Harry Potter fantasy series."
            }
        ]

        authors = {}
        for a_info in authors_data:
            author, _ = Author.objects.get_or_create(
                name=a_info["name"],
                defaults={"biography": a_info["biography"]}
            )
            authors[author.name] = author

        self.stdout.write(f"Created {len(authors)} authors.")

        # 2. Books
        books_data = [
            {
                "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
                "author": authors["Robert C. Martin"],
                "isbn": "978-0132350884",
                "genre": "Computer Science",
                "total_copies": 4,
                "available_copies": 2,  # 2 active loans
                "cover_url": "https://images.unsplash.com/photo-1532012164546-f432f2e3777a?auto=format&fit=crop&w=600&q=80",
                "description": "Even bad code can function. But if code isn't clean, it can bring a development organization to its knees. A revolutionary guide to writing elegant and maintainable code."
            },
            {
                "title": "Dune (Deluxe Collector's Edition)",
                "author": authors["Frank Herbert"],
                "isbn": "978-0441172719",
                "genre": "Sci-Fi",
                "total_copies": 3,
                "available_copies": 0,  # OUT OF STOCK! Perfect for testing out-of-stock validation
                "cover_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=600&q=80",
                "description": "Set on the desert planet Arrakis, Dune tells the story of Paul Atreides and is widely considered the greatest science fiction saga of all time."
            },
            {
                "title": "Sapiens: A Brief History of Humankind",
                "author": authors["Yuval Noah Harari"],
                "isbn": "978-0062316097",
                "genre": "History",
                "total_copies": 5,
                "available_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=600&q=80",
                "description": "From a renowned historian comes a groundbreaking narrative of humanity's creation and evolution, exploring how biology and history have defined us."
            },
            {
                "title": "Refactoring: Improving the Design of Existing Code",
                "author": authors["Martin Fowler"],
                "isbn": "978-0134757599",
                "genre": "Computer Science",
                "total_copies": 3,
                "available_copies": 2,
                "cover_url": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=600&q=80",
                "description": "Fully updated for modern programming paradigms, Refactoring explains the principles and best techniques of refactoring legacy codebases."
            },
            {
                "title": "1984 (Nineteen Eighty-Four)",
                "author": authors["George Orwell"],
                "isbn": "978-0451524935",
                "genre": "Fiction",
                "total_copies": 6,
                "available_copies": 5,
                "cover_url": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=600&q=80",
                "description": "The dystopian masterpiece about Winston Smith, Big Brother, the Thought Police, and totalitarian surveillance state control."
            },
            {
                "title": "Steve Jobs: The Exclusive Biography",
                "author": authors["Walter Isaacson"],
                "isbn": "978-1451648539",
                "genre": "Biography",
                "total_copies": 4,
                "available_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80",
                "description": "Based on more than forty interviews with Jobs conducted over two years, Isaacson's riveting biography reveals the eccentric visionary behind Apple."
            },
            {
                "title": "Cosmos: The Story of Cosmic Evolution",
                "author": authors["Carl Sagan"],
                "isbn": "978-0345331359",
                "genre": "Science",
                "total_copies": 5,
                "available_copies": 4,
                "cover_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=600&q=80",
                "description": "A magnificent exploration of science and civilization tracing fifteen billion years of cosmic evolution that transformed matter into consciousness."
            },
            {
                "title": "Harry Potter and the Sorcerer's Stone",
                "author": authors["J.K. Rowling"],
                "isbn": "978-0590353427",
                "genre": "Fiction",
                "total_copies": 6,
                "available_copies": 4,
                "cover_url": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80",
                "description": "Harry Potter has never even heard of Hogwarts when the letters start dropping on the doormat at number four, Privet Drive."
            },
            {
                "title": "The Clean Coder: A Code of Conduct for Professional Programmers",
                "author": authors["Robert C. Martin"],
                "isbn": "978-0137081073",
                "genre": "Computer Science",
                "total_copies": 3,
                "available_copies": 2,
                "cover_url": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=600&q=80",
                "description": "Presents practical advice about estimating, coding, refactoring, and testing for software professionals aspiring to mastery."
            },
            {
                "title": "Animal Farm: A Fairy Story",
                "author": authors["George Orwell"],
                "isbn": "978-0451526342",
                "genre": "Fiction",
                "total_copies": 4,
                "available_copies": 4,
                "cover_url": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=600&q=80",
                "description": "A biting political allegory about the animals of Manor Farm who overthrow their human master only to find themselves under new tyrants."
            },
            {
                "title": "Leonardo da Vinci",
                "author": authors["Walter Isaacson"],
                "isbn": "978-1501139154",
                "genre": "Biography",
                "total_copies": 2,
                "available_copies": 1,
                "cover_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80",
                "description": "He was history's most creative genius. What secrets can he teach us? Isaacson weaves Leonardo's art with his science."
            },
            {
                "title": "Pale Blue Dot: A Vision of the Human Future in Space",
                "author": authors["Carl Sagan"],
                "isbn": "978-0345376596",
                "genre": "Science",
                "total_copies": 3,
                "available_copies": 3,
                "cover_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?auto=format&fit=crop&w=600&q=80",
                "description": "Pulitzer Prize-winning author Carl Sagan traces the spellbinding history of our launch into the cosmos and assesses our destiny."
            }
        ]

        books = {}
        for b_info in books_data:
            book, _ = Book.objects.get_or_create(
                isbn=b_info["isbn"],
                defaults=b_info
            )
            books[book.title] = book

        self.stdout.write(f"Created {len(books)} books.")

        # 3. Members
        members_data = [
            {
                "name": "Sarah Connor",
                "member_id": "MEM-1001",
                "email": "sarah.connor@example.com",
                "phone": "+1 (555) 234-5678",
                "joined_date": timezone.now().date() - datetime.timedelta(days=120)
            },
            {
                "name": "Alex Mercer",
                "member_id": "MEM-1002",
                "email": "alex.mercer@example.com",
                "phone": "+1 (555) 345-6789",
                "joined_date": timezone.now().date() - datetime.timedelta(days=90)
            },
            {
                "name": "Elena Rostova",
                "member_id": "MEM-1003",
                "email": "elena.rostova@example.com",
                "phone": "+1 (555) 456-7890",
                "joined_date": timezone.now().date() - datetime.timedelta(days=60)
            },
            {
                "name": "Marcus Vance",
                "member_id": "MEM-1004",
                "email": "marcus.vance@example.com",
                "phone": "+1 (555) 567-8901",
                "joined_date": timezone.now().date() - datetime.timedelta(days=45)
            },
            {
                "name": "Priya Sharma",
                "member_id": "MEM-1005",
                "email": "priya.sharma@example.com",
                "phone": "+1 (555) 678-9012",
                "joined_date": timezone.now().date() - datetime.timedelta(days=15)
            }
        ]

        members = {}
        for m_info in members_data:
            member, _ = Member.objects.get_or_create(
                member_id=m_info["member_id"],
                defaults=m_info
            )
            members[member.name] = member

        self.stdout.write(f"Created {len(members)} members.")

        # 4. Circulation Records
        today = timezone.now().date()

        # (a) Active Loan - On Schedule (Sarah Connor -> Clean Code)
        # Issued 5 days ago, due in 9 days
        CirculationRecord.objects.create(
            book=books["Clean Code: A Handbook of Agile Software Craftsmanship"],
            member=members["Sarah Connor"],
            issue_date=today - datetime.timedelta(days=5),
            due_date=today - datetime.timedelta(days=5) + datetime.timedelta(days=14),
            returned=False,
            notes="Standard loan for software engineering student"
        )

        # (b) OVERDUE Active Loan (Alex Mercer -> Dune)
        # Issued 25 days ago, due 11 days ago! Overdue by 11 days -> Fine is $11.00!
        CirculationRecord.objects.create(
            book=books["Dune (Deluxe Collector's Edition)"],
            member=members["Alex Mercer"],
            issue_date=today - datetime.timedelta(days=25),
            due_date=today - datetime.timedelta(days=11),
            returned=False,
            notes="Urgent overdue notice emailed"
        )

        # (c) Another Active Loan for Dune (All 3 copies of Dune are checked out: 3 total, 0 available)
        CirculationRecord.objects.create(
            book=books["Dune (Deluxe Collector's Edition)"],
            member=members["Elena Rostova"],
            issue_date=today - datetime.timedelta(days=18),
            due_date=today - datetime.timedelta(days=4),  # Overdue by 4 days! Fine $4.00
            returned=False,
            notes="Follow up due date"
        )
        CirculationRecord.objects.create(
            book=books["Dune (Deluxe Collector's Edition)"],
            member=members["Marcus Vance"],
            issue_date=today - datetime.timedelta(days=4),
            due_date=today + datetime.timedelta(days=10),
            returned=False,
            notes="Active reading club loan"
        )

        # (d) Active Loan - On Schedule (Priya Sharma -> Sapiens)
        CirculationRecord.objects.create(
            book=books["Sapiens: A Brief History of Humankind"],
            member=members["Priya Sharma"],
            issue_date=today - datetime.timedelta(days=2),
            due_date=today + datetime.timedelta(days=12),
            returned=False,
            notes="History freshman assignment"
        )

        # (e) Active Loan - On Schedule (Alex Mercer -> Sapiens)
        CirculationRecord.objects.create(
            book=books["Sapiens: A Brief History of Humankind"],
            member=members["Alex Mercer"],
            issue_date=today - datetime.timedelta(days=6),
            due_date=today + datetime.timedelta(days=8),
            returned=False,
            notes="General loan"
        )

        # (f) Past Returned Loan - On Time ($0 Fine)
        CirculationRecord.objects.create(
            book=books["Refactoring: Improving the Design of Existing Code"],
            member=members["Sarah Connor"],
            issue_date=today - datetime.timedelta(days=40),
            due_date=today - datetime.timedelta(days=26),
            return_date=today - datetime.timedelta(days=28),
            fine_amount=Decimal('0.00'),
            returned=True,
            notes="Returned in mint condition"
        )

        # (g) Past Returned Loan - Overdue ($5.00 Fine Paid)
        CirculationRecord.objects.create(
            book=books["Cosmos: The Story of Cosmic Evolution"],
            member=members["Elena Rostova"],
            issue_date=today - datetime.timedelta(days=35),
            due_date=today - datetime.timedelta(days=21),
            return_date=today - datetime.timedelta(days=16),  # 5 days late
            fine_amount=Decimal('5.00'),
            returned=True,
            notes="Fine paid in full via library counter"
        )

        # (h) Past Returned Loan - Overdue ($8.00 Fine Paid)
        CirculationRecord.objects.create(
            book=books["Harry Potter and the Sorcerer's Stone"],
            member=members["Marcus Vance"],
            issue_date=today - datetime.timedelta(days=50),
            due_date=today - datetime.timedelta(days=36),
            return_date=today - datetime.timedelta(days=28),  # 8 days late
            fine_amount=Decimal('8.00'),
            returned=True,
            notes="Fine settled"
        )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded with realistic sample data!"))
