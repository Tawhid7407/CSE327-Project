"""
Unit tests for the accounts app.
"""

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .decorators import admin_required, doctor_required, patient_required
from .forms import RegisterForm
from .models import User


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def create_patient(username="patient1", password="test-pass-123", **extra):
    """Create a patient user."""
    return User.objects.create_user(
        username=username,
        password=password,
        role="patient",
        **extra,
    )


def create_doctor(
    username="doctor1",
    password="test-pass-123",
    approved=True,
    **extra
):
    """Create a doctor user."""
    return User.objects.create_user(
        username=username,
        password=password,
        role="doctor",
        is_approved=approved,
        **extra,
    )


def create_admin(username="admin1", password="test-pass-123", **extra):
    """Create an admin user."""
    return User.objects.create_user(
        username=username,
        password=password,
        role="admin",
        **extra,
    )


# ---------------------------------------------------------
# User role tests
# ---------------------------------------------------------

class UserRoleTests(TestCase):

    def test_patient_role(self):
        user = User(role="patient")

        self.assertTrue(user.is_patient())
        self.assertFalse(user.is_doctor())
        self.assertFalse(user.is_admin_user())

    def test_doctor_role(self):
        user = User(role="doctor")

        self.assertTrue(user.is_doctor())
        self.assertFalse(user.is_patient())

    def test_admin_role(self):
        user = User(role="admin")

        self.assertTrue(user.is_admin_user())

    def test_superuser_is_admin(self):
        user = User(
            role="patient",
            is_superuser=True,
        )

        self.assertTrue(user.is_admin_user())


# ---------------------------------------------------------
# Authentication decorator tests
# ---------------------------------------------------------

class DecoratorTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        @patient_required
        def patient_view(request):
            return HttpResponse("OK")

        @doctor_required
        def doctor_view(request):
            return HttpResponse("OK")

        @admin_required
        def admin_view(request):
            return HttpResponse("OK")

        self.patient_view = patient_view
        self.doctor_view = doctor_view
        self.admin_view = admin_view

    def make_request(self, user):
        request = self.factory.get("/test/")

        request.user = user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        return request

    def test_patient_required_blocks_anonymous(self):
        response = self.patient_view(
            self.make_request(AnonymousUser())
        )

        self.assertEqual(response.status_code, 302)

    def test_patient_required_blocks_doctor(self):
        doctor = create_doctor()

        response = self.patient_view(
            self.make_request(doctor)
        )

        self.assertEqual(response.status_code, 302)

    def test_patient_required_allows_patient(self):
        patient = create_patient()

        response = self.patient_view(
            self.make_request(patient)
        )

        self.assertEqual(response.status_code, 200)

    def test_doctor_required_blocks_unapproved_doctor(self):
        doctor = create_doctor(approved=False)

        response = self.doctor_view(
            self.make_request(doctor)
        )

        self.assertEqual(response.status_code, 302)

    def test_doctor_required_allows_approved_doctor(self):
        doctor = create_doctor(approved=True)

        response = self.doctor_view(
            self.make_request(doctor)
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_required_allows_superuser(self):
        user = create_patient(username="superuser")

        user.is_superuser = True
        user.save()

        response = self.admin_view(
            self.make_request(user)
        )

        self.assertEqual(response.status_code, 200)


# ---------------------------------------------------------
# Registration form tests
# ---------------------------------------------------------

class RegisterFormTests(TestCase):

    def valid_data(self, role="patient", email="new@example.com"):
        return {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": email,
            "phone": "01700000000",
            "role": role,
            "password1": "S0meStrongPass!",
            "password2": "S0meStrongPass!",
        }

    def test_patient_registration(self):
        form = RegisterForm(self.valid_data())

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        user = form.save()

        self.assertEqual(user.role, "patient")
        self.assertTrue(user.is_approved)

    def test_doctor_registration_requires_approval(self):
        form = RegisterForm(
            self.valid_data(role="doctor")
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        user = form.save()

        self.assertEqual(user.role, "doctor")
        self.assertFalse(user.is_approved)

    def test_duplicate_email_is_rejected(self):
        create_patient(
            username="existing",
            email="duplicate@example.com",
        )

        form = RegisterForm(
            self.valid_data(
                email="duplicate@example.com"
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


# ---------------------------------------------------------
# Role redirect tests
# ---------------------------------------------------------

class RoleRedirectTests(TestCase):

    def login_and_redirect(self, user):
        self.client.force_login(user)

        return self.client.get(
            reverse("accounts:role_redirect")
        )

    def test_admin_redirect(self):
        user = create_admin()

        response = self.login_and_redirect(user)

        self.assertEqual(response.status_code, 302)

    def test_doctor_redirect(self):
        user = create_doctor()

        response = self.login_and_redirect(user)

        self.assertEqual(response.status_code, 302)

    def test_patient_redirect(self):
        user = create_patient()

        response = self.login_and_redirect(user)

        self.assertEqual(response.status_code, 302)

    def test_superuser_redirect(self):
        user = create_patient(
            username="superuser"
        )

        user.is_superuser = True
        user.save()

        response = self.login_and_redirect(user)

        self.assertEqual(response.status_code, 302)