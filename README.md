# 🏥 MediConnect — Doctor Appointment System

A Django-based Doctor Appointment Management System with 3 user roles: Admin, Doctor, and Patient.

## 🚀 Setup Instructions

### 1. Install Python
Make sure Python 3.10+ is installed.

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **Linux/Mac:** `source venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
When creating, use role = `admin`. Or run the seeder below.

### 6. Load Sample Data (Optional but Recommended)
```bash
python manage.py seed_data
```
This creates:
- Admin: `admin` / `admin123`
- Doctor: `doctor1` / `doctor123` (approved)
- Patient: `patient1` / `patient123`
- Sample departments and appointments

### 7. Run the Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

## 🔑 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `doctor1` | `doctor123` |
| Patient | `patient1` | `patient123` |

## 📂 URLs

- Homepage: `/`
- Login: `/accounts/login/`
- Register: `/accounts/register/`
- Admin Panel: `/admin-panel/dashboard/`
- Django Admin: `/admin/`

## ✨ Features

- ✅ 3 User Roles (Admin/Doctor/Patient)
- ✅ Doctor approval workflow
- ✅ Department management
- ✅ Doctor availability schedule
- ✅ Appointment booking system
- ✅ Prescription management
- ✅ Medical history
- ✅ Dashboard-based notifications
- ✅ Review & rating system
- ✅ Contact/Feedback form
- ✅ Reports & statistics
- ✅ Responsive Bootstrap 5 UI

## 🛠️ Tech Stack

- Backend: Django 4.2
- Frontend: Bootstrap 5, HTML5, CSS3, JavaScript
- Database: SQLite (default)
- Auth: Django built-in (email-based password reset)

## 🧪 Running Tests

Unit tests use Django's built-in test framework (`django.test.TestCase`,
built on Python's `unittest`) — no extra install needed.

```bash
python manage.py test            # run the whole suite
python manage.py test reviews    # run one app's tests only
```

## 📧 Email Configuration (Optional)

For password reset via email, edit `mediconnect/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

By default, emails are printed to the console (dev mode).
