"""
Unit tests for the medical_history app: creating records and the
ownership check on history_delete() (a patient must not be able to
delete another patient's record).
"""
import datetime

from django.test import TestCase
from django.urls import reverse

from mediconnect.test_helpers import make_patient
from .models import MedicalHistory


class HistoryCreateViewTests(TestCase):
    def setUp(self):
        self.patient = make_patient()
        self.client.login(username=self.patient.user.username, password='test-pass-123')

    def test_valid_data_creates_record(self):
        response = self.client.post(reverse('medical_history:create'), {
            'condition': 'Asthma',
            'diagnosed_date': datetime.date(2020, 1, 1),
            'notes': 'Mild, controlled with inhaler.',
        })
        self.assertRedirects(response, reverse('medical_history:list'))
        self.assertEqual(MedicalHistory.objects.count(), 1)
        self.assertEqual(MedicalHistory.objects.first().patient, self.patient)


class HistoryDeleteOwnershipTests(TestCase):
    """Equivalence Partitioning: own record (valid) vs. someone else's (invalid)."""

    def setUp(self):
        self.owner = make_patient(username='owner')
        self.other = make_patient(username='other')
        self.record = MedicalHistory.objects.create(
            patient=self.owner, condition='Asthma',
            diagnosed_date=datetime.date(2020, 1, 1),
        )

    def test_owner_can_delete_own_record(self):
        self.client.login(username=self.owner.user.username, password='test-pass-123')
        self.client.post(reverse('medical_history:delete', args=[self.record.pk]))
        self.assertFalse(MedicalHistory.objects.filter(pk=self.record.pk).exists())

    def test_other_patient_cannot_delete_it(self):
        self.client.login(username=self.other.user.username, password='test-pass-123')
        response = self.client.post(reverse('medical_history:delete', args=[self.record.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(MedicalHistory.objects.filter(pk=self.record.pk).exists())
