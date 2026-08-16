"""Unit tests for the patients app."""
from django.test import TestCase
from django.urls import reverse

from mediconnect.test_helpers import make_doctor, make_patient


class PatientProfileModelTests(TestCase):
    def test_str_falls_back_to_username_without_full_name(self):
        patient = make_patient(username='janedoe')
        self.assertEqual(str(patient), 'janedoe')

    def test_str_uses_full_name_when_available(self):
        patient = make_patient(username='janedoe2', first_name='Jane', last_name='Doe')
        self.assertEqual(str(patient), 'Jane Doe')


class PatientDashboardViewTests(TestCase):
    def test_requires_patient_role(self):
        doctor = make_doctor()
        self.client.login(username=doctor.user.username, password='test-pass-123')
        response = self.client.get(reverse('patients:dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_patient_can_view_own_dashboard(self):   //uploded new file
        patient = make_patient()
        self.client.login(username=patient.user.username, password='test-pass-123')
        response = self.client.get(reverse('patients:dashboard'))
        self.assertEqual(response.status_code, 200)
