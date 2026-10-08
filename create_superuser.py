import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hruthika.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from circulation.models import Book

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

# 1. Create superuser if not existing
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' successfully created.")
else:
    print(f"Superuser '{username}' already exists. Skipping creation.")

# 2. Automatically seed initial sample books and members if database is empty on Render
if Book.objects.count() == 0:
    print("Database has 0 books. Seeding sample library catalog and records...")
    call_command('seed_data')
else:
    print(f"Database contains {Book.objects.count()} existing books. Skipping seed.")
