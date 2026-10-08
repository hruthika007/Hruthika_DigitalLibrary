# Digital Library & E-Book Circulation Portal

**Django Full-Stack Final Project — Capstone Project 3**

A digital library circulation web application where users browse books, filter by genre or availability, search the catalog with instant client-side responsiveness, issue and return books with automated 14-day due date tracking, and calculate overdue fines ($1.00/day).

---

## 🌟 Key Features

1. **Book Catalog with Live Instant Search & Badges**
   - High-resolution book covers with genre tags, author information, ISBN, and real-time inventory badges.
   - Client-side instant live search across Title, Author, Genre, and ISBN without page reloads.
   - Genre filter chips (*Computer Science, Fiction, Sci-Fi, Science, Biography, History*).
   - Inventory availability filter (*All, In Stock Only, Out of Stock Only*).
   - Out-of-stock guard prevents checking out books with zero available copies.

2. **Circulation Hub & Issuing Workflow**
   - Direct "Issue Book" action pre-selected from catalog cards or custom selection.
   - Automatically computes and sets the official **Due Date to 14 days after issue**.
   - Reduces `available_copies` by 1 upon issuance.
   - Live interactive due-date preview with countdown.

3. **Return Workflow & Overdue Fine Calculation**
   - Automated check-in workflow restoring book stock (`available_copies + 1`).
   - Dynamic return date simulator computing days overdue and fine amount ($1.00 per day).
   - Updates record with final fine amount, marks loan as `returned=True`.

4. **Member Dashboard & Patron Profiles**
   - Individual patron dashboards showing active borrowed items and historical loans.
   - Real-time **Overdue Warning Alerts** highlighting overdue books and accumulated fine balances.
   - Complete borrowing history with return timestamps and fines settled.

5. **Interactive Due-Date & Overdue Fine Calculator**
   - Standalone interactive tool with sliders and date pickers for quick mathematical simulations.
   - Visual breakdown of loan duration, grace period, overdue days, and formula mechanics.

6. **Django Admin Management**
   - Pre-configured admin interface at `/admin/` for `Author`, `Book`, `Member`, and `CirculationRecord`.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Django 6.x, Django ORM
- **Database**: SQLite (`db.sqlite3`)
- **Frontend**: HTML5, CSS3 (Modern Glassmorphism & Tokens), JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons
- **Production & Deployment**: Gunicorn, WhiteNoise, Render Blueprint (`render.yaml`)

---

## 🚀 Local Development Setup

### 1. Clone & Navigate to Repository
```bash
git clone <repository_url>
cd Hruthika
```

### 2. Activate Virtual Environment
**Windows (PowerShell):**
```powershell
.\venv\Scripts\activate
```
**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_data
```

### 5. Create Superuser (Admin)
```bash
python create_superuser.py
```
*Default credentials:*
- **Username:** `admin`
- **Password:** `admin123`

### 6. Start Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser.

---

## 🧪 Running Automated Unit Tests
To verify all business logic rules, constraints, and views:
```bash
python manage.py test circulation
```

---

## ☁️ Render Deployment Guide

This project is configured for one-click deployment on **Render**:

1. Push this repository to GitHub:
   ```bash
   git add .
   git commit -m "Prepare Django project for Render"
   git push origin main
   ```
2. Log in to [Render](https://render.com).
3. Click **New +** → **Blueprint** (or **Web Service**).
4. Connect your GitHub repository.
5. Render will automatically detect `render.yaml` with the following configuration:
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py`
   - **Start Command**: `python manage.py migrate && python create_superuser.py && gunicorn Hruthika.wsgi:application`
6. Add environment variable `SECRET_KEY` in the Render dashboard if desired.
7. Click **Apply / Deploy** and access your live deployment URL (`https://<service-name>.onrender.com`).
