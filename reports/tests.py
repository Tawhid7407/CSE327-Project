"""
Tests for the reports app.
"""

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from mediconnect.test_helpers import make_admin, make_doctor, make_patient
from notifications.models import Notification


class AdminDashboardAccessTests(TestCase):

    def test_user_not_logged_in(self):
        response = self.client.get(
            reverse("reports:admin_dashboard")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_patient_cannot_access_dashboard(self):
        patient = make_patient()

        self.client.login(
            username=patient.user.username,
            password="test-pass-123"
        )

        response = self.client.get(
            reverse("reports:admin_dashboard")
        )

        self.assertNotEqual(response.status_code, 200)

    def test_admin_can_access_dashboard(self):
        admin = make_admin()

        self.client.login(
            username=admin.username,
            password="test-pass-123"
        )

        response = self.client.get(
            reverse("reports:admin_dashboard")
        )

        self.assertEqual(response.status_code, 200)


class ApproveDoctorViewTests(TestCase):

    def test_admin_can_approve_doctor(self):
        admin = make_admin()
        doctor = make_doctor(approved=False)

        self.client.login(
            username=admin.username,
            password="test-pass-123"
        )

        response = self.client.post(
            reverse(
                "reports:approve_doctor",
                args=[doctor.user.pk]
            )
        )

        self.assertRedirects(
            response,
            reverse("reports:doctor_management")
        )

        doctor.user.refresh_from_db()

        self.assertTrue(doctor.user.is_approved)

        notification_exists = Notification.objects.filter(
            user=doctor.user
        ).exists()

        self.assertTrue(notification_exists)


class RejectDoctorViewTests(TestCase):

    def test_admin_can_reject_doctor(self):
        admin = make_admin()
        doctor = make_doctor(approved=False)

        user_pk = doctor.user.pk

        self.client.login(
            username=admin.username,
            password="test-pass-123"
        )

        response = self.client.post(
            reverse(
                "reports:reject_doctor",
                args=[user_pk]
            )
        )

        self.assertRedirects(
            response,
            reverse("reports:doctor_management")
        )

        user_exists = User.objects.filter(
            pk=user_pk
        ).exists()

        self.assertFalse(user_exists)