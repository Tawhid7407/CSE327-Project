"""
Unit tests for the appointments app.

Demonstrates Black Box techniques from Lecture 11/12:

- AppointmentDateBoundaryTests: Boundary Value Analysis on
  AppointmentForm.clean_appointment_date(), whose boundary is "today"
  (date < timezone.localdate() is rejected).
- StatusBadgeEquivalenceTests: "member of a set" Equivalence Partitioning
  over Appointment.STATUS_CHOICES.
- CancelAppointmentStatusTests: Equivalence Partitioning of
  cancel_appointment() over the status set -> {pending, approved} is the
  valid (cancellable) partition, everything else is invalid.
- AppointmentActionTests: "member of a set" partition on the
  appointment_action() valid-action dict.
"""
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from mediconnect.test_helpers import make_doctor, make_patient
from notifications.models import Notification
from .forms import AppointmentForm
from .models import Appointment


class AppointmentDateBoundaryTests(TestCase):
    """Boundary Value Analysis: boundary = today (X)."""

    def _form(self, date):
        return AppointmentForm(data={
            'appointment_date': date,
            'appointment_time': '10:00',
            'reason': 'Checkup',
        })

    def test_yesterday_is_invalid(self):
        yesterday = timezone.localdate() - datetime.timedelta(days=1)
        form = self._form(yesterday)
        self.assertFalse(form.is_valid())
        self.assertIn('appointment_date', form.errors)

    def test_today_is_valid_boundary(self):
        today = timezone.localdate()
        form = self._form(today)
        self.assertTrue(form.is_valid(), form.errors)

    def test_tomorrow_is_valid(self):
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        form = self._form(tomorrow)
        self.assertTrue(form.is_valid(), form.errors)


class StatusBadgeEquivalenceTests(TestCase):
    """status_badge property: one test per member of the status set."""

    def setUp(self):
        self.doctor = make_doctor()
        self.patient = make_patient()

    def _appointment(self, status):
        return Appointment(
            patient=self.patient, doctor=self.doctor,
            appointment_date=timezone.localdate(),
            appointment_time=datetime.time(9, 0),
            reason='x', status=status,
        )

    def test_pending_badge_is_warning(self):
        self.assertEqual(self._appointment('pending').status_badge, 'warning')

    def test_approved_badge_is_primary(self):
        self.assertEqual(self._appointment('approved').status_badge, 'primary')

    def test_rejected_badge_is_danger(self):
        self.assertEqual(self._appointment('rejected').status_badge, 'danger')

    def test_completed_badge_is_success(self):
        self.assertEqual(self._appointment('completed').status_badge, 'success')

    def test_cancelled_badge_is_secondary(self):
        self.assertEqual(self._appointment('cancelled').status_badge, 'secondary')


class BookAppointmentViewTests(TestCase):
    def setUp(self):
        self.doctor = make_doctor()
        self.patient = make_patient()
        self.client.login(username=self.patient.user.username, password='test-pass-123')

    def test_valid_booking_creates_appointment_and_notifies_doctor(self):
        url = reverse('appointments:book', args=[self.doctor.pk])
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        response = self.client.post(url, {
            'appointment_date': tomorrow,
            'appointment_time': '11:30',
            'reason': 'Fever and cough',
        })
        self.assertRedirects(response, reverse('appointments:my_appointments'))
        self.assertEqual(Appointment.objects.count(), 1)
        appt = Appointment.objects.first()
        self.assertEqual(appt.status, 'pending')
        self.assertTrue(
            Notification.objects.filter(user=self.doctor.user).exists()
        )


class CancelAppointmentStatusTests(TestCase):
    """Equivalence Partitioning over status: cancellable vs not-cancellable."""

    def setUp(self):
        self.doctor = make_doctor()
        self.patient = make_patient()
        self.client.login(username=self.patient.user.username, password='test-pass-123')

    def _make_appointment(self, status):
        return Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            appointment_date=timezone.localdate(),
            appointment_time=datetime.time(9, 0),
            reason='x', status=status,
        )

    def test_pending_is_cancellable(self):
        appt = self._make_appointment('pending')
        self.client.post(reverse('appointments:cancel', args=[appt.pk]))
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'cancelled')

    def test_approved_is_cancellable(self):
        appt = self._make_appointment('approved')
        self.client.post(reverse('appointments:cancel', args=[appt.pk]))
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'cancelled')

    def test_completed_is_not_cancellable(self):
        appt = self._make_appointment('completed')
        self.client.post(reverse('appointments:cancel', args=[appt.pk]))
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'completed')  # unchanged


class AppointmentActionTests(TestCase):
    """'Member of a set' partition on appointment_action()'s valid actions."""

    def setUp(self):
        self.doctor = make_doctor()
        self.patient = make_patient()
        self.appt = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor,
            appointment_date=timezone.localdate(),
            appointment_time=datetime.time(9, 0),
            reason='x', status='pending',
        )
        self.client.login(username=self.doctor.user.username, password='test-pass-123')

    def test_valid_action_updates_status(self):
        url = reverse('appointments:action', args=[self.appt.pk, 'approve'])
        self.client.post(url)
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, 'approved')

    def test_invalid_action_is_rejected(self):
        url = reverse('appointments:action', args=[self.appt.pk, 'delete'])
        self.client.post(url)
        self.appt.refresh_from_db()
        self.assertEqual(self.appt.status, 'pending')  # unchanged
