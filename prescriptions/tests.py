"""
Unit tests for the prescriptions app: Prescription.__str__, the
completed-appointment precondition on create_prescription(), and the
ownership check in prescription_detail().
"""
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from appointments.models import Appointment
from mediconnect.test_helpers import make_doctor, make_patient
from .models import Prescription


def _make_appointment(patient, doctor, status='completed'):
    return Appointment.objects.create(
        patient=patient, doctor=doctor,
        appointment_date=timezone.localdate(),
        appointment_time=datetime.time(9, 0),
        reason='x', status=status,
    )


class PrescriptionModelTests(TestCase):
    def test_str_mentions_patient(self):
        doctor = make_doctor()
        patient = make_patient()
        appt = _make_appointment(patient, doctor)
        presc = Prescription.objects.create(
            appointment=appt, diagnosis='Flu', medicines='Paracetamol'
        )
        self.assertIn(str(patient), str(presc))


class CreatePrescriptionPreconditionTests(TestCase):
    """Equivalence Partitioning on appointment.status: completed vs not."""

    def setUp(self):
        self.doctor = make_doctor()
        self.patient = make_patient()
        self.client.login(username=self.doctor.user.username, password='test-pass-123')

    def test_blocked_when_appointment_not_completed(self):
        appt = _make_appointment(self.patient, self.doctor, status='pending')
        response = self.client.post(
            reverse('prescriptions:create', args=[appt.pk]),
            {'diagnosis': 'Flu', 'medicines': 'Paracetamol', 'advice': ''},
        )
        self.assertRedirects(response, reverse('appointments:manage'))
        self.assertEqual(Prescription.objects.count(), 0)

    def test_allowed_when_appointment_completed(self):
        appt = _make_appointment(self.patient, self.doctor, status='completed')
        response = self.client.post(
            reverse('prescriptions:create', args=[appt.pk]),
            {'diagnosis': 'Flu', 'medicines': 'Paracetamol', 'advice': ''},
        )
        self.assertEqual(Prescription.objects.count(), 1)


class PrescriptionDetailAccessTests(TestCase):
    """Equivalence Partitioning: owner (patient/doctor/admin) vs stranger."""

    def setUp(self):
        self.doctor = make_doctor()
        self.patient = make_patient()
        appt = _make_appointment(self.patient, self.doctor)
        self.presc = Prescription.objects.create(
            appointment=appt, diagnosis='Flu', medicines='Paracetamol'
        )
        self.url = reverse('prescriptions:view', args=[self.presc.pk])

    def test_owning_patient_can_view(self):
        self.client.login(username=self.patient.user.username, password='test-pass-123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_unrelated_patient_is_denied(self):
        stranger = make_patient(username='stranger')
        self.client.login(username=stranger.user.username, password='test-pass-123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:home'))
