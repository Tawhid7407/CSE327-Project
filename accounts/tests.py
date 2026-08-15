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
from departments.models import Department
from doctors.models import DoctorProfile
from patients.models import PatientProfile


def make_patient(username="patient1", password="test-pass-123", **extra):
    user = User.objects.create_user(
        username=username,
        password=password,
        role="patient",
        **extra,
    )
    PatientProfile.objects.get_or_create(user=user)
    return PatientProfile.objects.get(user=user)


def make_doctor(
    username="doctor1",
    password="test-pass-123",
    approved=True,
    department=None,
    **extra,
):
    user = User.objects.create_user(
        username=username,
        password=password,
        role="doctor",
        is_approved=approved,
        **extra,
    )
    DoctorProfile.objects.get_or_create(
        user=user,
        defaults={"department": department},
    )
    return DoctorProfile.objects.get(user=user)


def make_admin(username="admin1", password="test-pass-123", **extra):
    return User.objects.create_user(
        username=username,
        password=password,
        role="admin",
        **extra,
    )


class UserRoleHelperTests(TestCase):
    def test_is_patient_true_for_patient_role(self):
        user = User(role='patient')
        self.assertTrue(user.is_patient())
        self.assertFalse(user.is_doctor())
        self.assertFalse(user.is_admin_user())

    def test_is_doctor_true_for_doctor_role(self):
        user = User(role='doctor')
        self.assertTrue(user.is_doctor())
        self.assertFalse(user.is_patient())

    def test_is_admin_user_true_for_admin_role(self):
        user = User(role='admin')
        self.assertTrue(user.is_admin_user())

    def test_is_admin_user_true_for_superuser_regardless_of_role(self):
        user = User(role='patient', is_superuser=True)
        self.assertTrue(user.is_admin_user())


class DecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        @patient_required
        def patient_view(request):
            return HttpResponse('ok')

        @doctor_required
        def doctor_view(request):
            return HttpResponse('ok')

        @admin_required
        def admin_view(request):
            return HttpResponse('ok')

        self.patient_view = patient_view
        self.doctor_view = doctor_view
        self.admin_view = admin_view

    def _request_as(self, user):
        request = self.factory.get('/dummy/')
        request.user = user
        request.session = SessionStore()
        request._messages = FallbackStorage(request)
        return request

    def test_patient_required_blocks_anonymous_user(self):
        response = self.patient_view(self._request_as(AnonymousUser()))
        self.assertEqual(response.status_code, 302)

    def test_patient_required_blocks_wrong_role(self):
        doctor = make_doctor().user
        response = self.patient_view(self._request_as(doctor))
        self.assertEqual(response.status_code, 302)

    def test_patient_required_allows_patient(self):
        patient = make_patient().user
        response = self.patient_view(self._request_as(patient))
        self.assertEqual(response.status_code, 200)

    def test_doctor_required_blocks_unapproved_doctor(self):
        doctor = make_doctor(approved=False).user
        response = self.doctor_view(self._request_as(doctor))
        self.assertEqual(response.status_code, 302)

    def test_doctor_required_allows_approved_doctor(self):
        doctor = make_doctor(approved=True).user
        response = self.doctor_view(self._request_as(doctor))
        self.assertEqual(response.status_code, 200)

    def test_admin_required_allows_superuser(self):
        user = make_patient(username='superpatient').user
        user.is_superuser = True
        user.save()

        response = self.admin_view(self._request_as(user))
        self.assertEqual(response.status_code, 200)


class RegisterFormTests(TestCase):
    def _valid_data(self, role='patient', email='new@example.com'):
        return {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': email,
            'phone': '01700000000',
            'role': role,
            'password1': 'S0meStrongPass!',
            'password2': 'S0meStrongPass!',
        }

    def test_patient_registration_is_auto_approved(self):
        form = RegisterForm(self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        self.assertTrue(user.is_approved)

    def test_doctor_registration_needs_approval(self):
        form = RegisterForm(self._valid_data(role='doctor'))
        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()
        self.assertFalse(user.is_approved)

    def test_duplicate_email_is_invalid(self):
        make_patient(username='existing', email='dup@example.com')

        form = RegisterForm(self._valid_data(email='dup@example.com'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class RoleRedirectViewTests(TestCase):
    def _login_and_hit(self, user):
        self.client.force_login(user)
        return self.client.get(reverse('accounts:role_redirect'))

    def test_admin_redirects_to_admin_dashboard(self):
        response = self._login_and_hit(make_admin())
        self.assertRedirects(
            response,
            reverse('reports:admin_dashboard'),
        )

    def test_doctor_redirects_to_doctor_dashboard(self):
        response = self._login_and_hit(make_doctor().user)
        self.assertRedirects(
            response,
            reverse('doctors:dashboard'),
        )

    def test_patient_redirects_to_patient_dashboard(self):
        response = self._login_and_hit(make_patient().user)
        self.assertRedirects(
            response,
            reverse('patients:dashboard'),
        )

    def test_superuser_redirects_to_admin_dashboard(self):
        user = make_patient(username='superuser')
        user = user.user
        user.is_superuser = True
        user.save()

        response = self._login_and_hit(user)

        self.assertRedirects(
            response,
            reverse('reports:admin_dashboard'),
        )