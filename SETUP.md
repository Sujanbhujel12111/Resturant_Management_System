# Restaurant Management System - Setup & Architecture

## 🏗️ Project Structure

```
Restaurant-Management-System/
├── .env                          # Environment variables (Supabase credentials)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── manage.py                     # Django management script
├── README.md                     # Project overview
│
├── restaurant_project/           # Main Django project
│   ├── settings/
│   │   ├── __init__.py
│   │   └── base.py              # All settings (PostgreSQL/Supabase)
│   ├── urls.py
│   ├── wsgi.py
│   └── __pycache__/
│
├── accounts/                     # User authentication & roles
│   ├── models.py                # User & Staff models
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── migrations/
│   └── templatetags/
│
├── restaurant/                   # Main app - Orders, Menu, Tables
│   ├── models.py                # Order, MenuItem, Category, Table, etc.
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── static/                  # CSS, JS files
│   ├── templates/               # HTML templates
│   ├── management/              # Custom Django commands
│   ├── ml/                      # Machine learning models
│   ├── migrations/              # Database schema changes
│   └── signals.py               # Django signals
│
└── static/                      # Static files (CSS, JS, images)
```

---

## 🗄️ Database Setup

### Current Configuration: **Supabase PostgreSQL (Cloud)**

**Instead of SQLite, the project now uses Supabase - a managed PostgreSQL service.**

#### Environment Variables (.env)
```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_HOST=your-project-ref.supabase.co
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

#### Settings Location
- **File:** `restaurant_project/settings/base.py`
- **Database Engine:** `django.db.backends.postgresql`
- **Credentials:** Loaded from `.env` via `python-decouple`

---

## ✅ Security Features

### 🔒 Row Level Security (RLS) Enabled
All public tables have RLS enabled:
- ✅ Sensitive columns (passwords, sessions) protected
- ✅ Authenticated user access only
- ✅ Production-ready security

### 🛡️ Database Policies
- Users can only access their own sessions
- Staff can view staff-related data
- Admin can manage all data

---

## 📚 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 3.2+ |
| **Database** | Supabase (PostgreSQL) |
| **ORM** | Django ORM |
| **Auth** | Django Auth + Custom User Model |
| **Frontend** | HTML5, CSS3, Bootstrap |
| **Python Version** | 3.8+ |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create `.env` with Supabase credentials:
```
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=your-project.supabase.co
DB_PORT=5432
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Start Development Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/`

---

## 📊 Key Models

### Accounts App
- **User** - Custom user model with restaurant permissions
- **Staff** - Staff members with roles
- **StaffPermission** - Permission management for staff

### Restaurant App
- **Category** - Menu categories (appetizers, mains, desserts, etc.)
- **MenuItem** - Individual menu items with pricing
- **Table** - Restaurant table management
- **Order** - Current orders
- **OrderHistory** - Historical order records
- **OrderHistoryItem** - Items in historical orders
- **OrderHistoryPayment** - Payment details for orders
- **Payment** - Payment method tracking

---

## 🔄 API Endpoints

### Authentication
- `GET /login/` - Login page
- `POST /login/` - User login
- `GET /logout/` - Logout
- `GET /accounts/profile/` - User profile

### Orders
- `GET /orders/` - List all orders
- `GET /order/<id>/` - Order details
- `POST /place_order_dine_in/` - Create dine-in order
- `POST /place_order_takeaway/` - Create takeaway order
- `POST /place_order_delivery/` - Create delivery order

### Menu Items
- `GET /menuitems/` - List menu items
- `GET /menuitem/<id>/` - Item details
- `POST /menuitem/create/` - Add new item

### Kitchen
- `GET /kitchen/` - Kitchen view (orders to prepare)

### Admin
- `GET /admin/` - Django admin panel

---

## 🛠️ Development Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver

# Start dev server on specific port
python manage.py runserver 0.0.0.0:8001
```

---

## 📁 Removed Files
Following cloud-first approach, **SQLite files have been removed**:
- ❌ `db.sqlite3` - Local database (not needed)
- ❌ Temporary migration scripts
- ❌ Temporary test scripts

All data is now in **Supabase PostgreSQL**.

---

## 📝 Environment-specific Settings

Create environment-specific settings files as needed:

**settings/development.py:**
```python
from .base import *
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

**settings/production.py:**
```python
from .base import *
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: v.split(','))
SECURE_SSL_REDIRECT = True
```

Update `manage.py` to use specific settings:
```bash
python manage.py runserver --settings=restaurant_project.settings.development
```

---

## 🔗 Useful Links

- [Supabase Dashboard](https://supabase.com)
- [Django Documentation](https://docs.djangoproject.com)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Django ORM QuerySet](https://docs.djangoproject.com/en/3.2/ref/models/querysets/)

---

## 📞 Support

For issues:
1. Check `.env` file has correct Supabase credentials
2. Verify Supabase project is active
3. Run migrations: `python manage.py migrate`
4. Check Django logs for errors

---

**Last Updated:** February 11, 2026
