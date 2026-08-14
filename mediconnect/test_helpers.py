"""
Shared helpers for building test fixtures across the test suite.

Kept in one place so every app's tests.py can create a patient/doctor/admin
user (with their profile) in one line instead of repeating the same
boilerplate in every test module.
"""
from accounts.models import User
from departments.models import Department
from doctors.models import DoctorProfile
from patients.models import PatientProfile

DEFAULT_PASSWORD = "test-pass-123"


def make_department(name="Cardiology"):
    return Department.objects.create(name=name)


def make_patient(username="patient1", password=DEFAULT_PASSWORD, **extra):
    user = User.objects.create_user(
        username=username, password=password, role="patient", **extra
    )
    profile, _ = PatientProfile.objects.get_or_create(user=user)
    return profile


def make_doctor(username="doctor1", password=DEFAULT_PASSWORD, approved=True,
                 department=None, **extra):
    user = User.objects.create_user(
        username=username, password=password, role="doctor",
        is_approved=approved, **extra
    )
    profile, _ = DoctorProfile.objects.get_or_create(
        user=user, defaults={"department": department}
    )
    return profile


def make_admin(username="admin1", password=DEFAULT_PASSWORD, **extra):
    return User.objects.create_user(
        username=username, password=password, role="admin", **extra
    )
