"""
Unit tests for the reports app: admin-only access and the doctor
approve/reject actions.
"""
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from mediconnect.test_helpers import make_admin, make_doctor, make_patient
from notifications.models import Notification


class AdminDashboardAccessTests(TestCase):
    def test_anonymous_is_redirected(self):
        response = self.client.get(reverse('reports:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_non_admin_is_redirected(self):
        patient = make_patient()
        self.client.login(username=patient.user.username, password='test-pass-123')
        response = self.client.get(reverse('reports:admin_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_admin_can_view(self):
        admin = make_admin()
        self.client.login(username=admin.username, password='test-pass-123')
        response = self.client.get(reverse('reports:admin_dashboard'))
        self.assertEqual(response.status_code, 200)


class ApproveDoctorViewTests(TestCase):
    def test_approving_sets_flag_and_notifies(self):
        admin = make_admin()
        doctor = make_doctor(approved=False)
        self.client.login(username=admin.username, password='test-pass-123')
        response = self.client.post(reverse('reports:approve_doctor', args=[doctor.user.pk]))
        self.assertRedirects(response, reverse('reports:doctor_management'))
        doctor.user.refresh_from_db()
        self.assertTrue(doctor.user.is_approved)
        self.assertTrue(Notification.objects.filter(user=doctor.user).exists())


class RejectDoctorViewTests(TestCase):
    def test_rejecting_deletes_the_user(self):
        admin = make_admin()
        doctor = make_doctor(approved=False)
        user_pk = doctor.user.pk
        self.client.login(username=admin.username, password='test-pass-123')
        response = self.client.post(reverse('reports:reject_doctor', args=[user_pk]))
        self.assertRedirects(response, reverse('reports:doctor_management'))
        self.assertFalse(User.objects.filter(pk=user_pk).exists())
