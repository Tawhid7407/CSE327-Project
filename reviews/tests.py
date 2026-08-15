"""
Unit tests for the reviews app.

Two Lecture 11/12 techniques are demonstrated here on real project code:

1. White Box Testing (Control Flow Graph / Cyclomatic Complexity / Basic
   Path Testing) applied to ``submit_review()`` in reviews/views.py, which
   has 3 predicates (has_completed check, request.method == 'POST' check,
   form.is_valid() check) -> Cyclomatic Complexity = 3 + 1 = 4, hence the
   4 tests in SubmitReviewPathTests below, one per basic path.

2. Black Box Testing (Equivalence Partitioning + Boundary Value Analysis)
   applied to Review.rating, which is validated to the closed range [1..5]
   -> ReviewRatingBoundaryTests below.
"""
import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from appointments.models import Appointment
from mediconnect.test_helpers import make_doctor, make_patient
from .models import Review


class ReviewRatingBoundaryTests(TestCase):
    """Equivalence Partitioning + Boundary Value Analysis on rating [1..5].

    Partitions: [-inf..0] Invalid, [1..5] Valid, [6..inf] Invalid.
    Boundary values tested (X=1, Y=5): {0, 1, 5, 6}.
    """

    @classmethod
    def setUpTestData(cls):
        cls.doctor = make_doctor()
        cls.patient = make_patient()

    def _review(self, rating):
        return Review(doctor=self.doctor, patient=self.patient, rating=rating)

    def test_rating_below_range_is_invalid(self):
        with self.assertRaises(ValidationError):
            self._review(0).full_clean()

    def test_rating_lower_boundary_is_valid(self):
        self._review(1).full_clean()  # must not raise

    def test_rating_upper_boundary_is_valid(self):
        self._review(5).full_clean()  # must not raise

    def test_rating_above_range_is_invalid(self):
        with self.assertRaises(ValidationError):
            self._review(6).full_clean()


class SubmitReviewPathTests(TestCase):
    """Basic Path Set coverage for submit_review() (Cyclomatic Complexity 4)."""

    def setUp(self):
        self.doctor = make_doctor()
        self.patient_profile = make_patient()
        self.url = reverse('reviews:submit', args=[self.doctor.pk])
        self.client.login(username=self.patient_profile.user.username,
                           password='test-pass-123')

    def _create_completed_appointment(self):
        return Appointment.objects.create(
            patient=self.patient_profile,
            doctor=self.doctor,
            appointment_date=datetime.date.today(),
            appointment_time=datetime.time(10, 0),
            reason="Checkup",
            status='completed',
        )

    def test_path_no_completed_appointment_blocks_review(self):
        """Path [1-2-3]: has_completed is False -> redirected away, no Review."""
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse('doctors:detail', args=[self.doctor.pk])
        )
        self.assertEqual(Review.objects.count(), 0)

    def test_path_get_request_shows_form(self):
        """Path [1-2-4-5-9-10]: completed appt exists, GET -> form rendered."""
        self._create_completed_appointment()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_path_post_invalid_form_reshows_form(self):
        """Path [1-2-4-5-6-7-10]: completed appt exists, POST with bad data."""
        self._create_completed_appointment()
        response = self.client.post(self.url, {'rating': '', 'comment': 'nice'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Review.objects.count(), 0)

    def test_path_post_valid_form_creates_review(self):
        """Path [1-2-4-5-6-7-8]: completed appt exists, POST with valid data."""
        self._create_completed_appointment()
        response = self.client.post(
            self.url, {'rating': 5, 'comment': 'Great doctor!'}
        )
        self.assertRedirects(
            response, reverse('doctors:detail', args=[self.doctor.pk])
        )
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.doctor, self.doctor)
        self.assertEqual(review.patient, self.patient_profile)
        self.assertEqual(review.rating, 5)
