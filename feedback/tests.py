"""Unit tests for the feedback app."""
from django.test import TestCase
from django.urls import reverse

from mediconnect.test_helpers import make_admin, make_patient
from .models import Feedback


class FeedbackModelTests(TestCase):
    def test_str_combines_subject_and_name(self):
        fb = Feedback.objects.create(
            name="Alice", email="a@example.com", subject="Bug report",
            message="Something is broken.",
        )
        self.assertEqual(str(fb), "Bug report - Alice")


class ContactViewTests(TestCase):
    def test_valid_submission_saves_feedback(self):
        response = self.client.post(reverse('feedback:contact'), {
            'name': 'Alice', 'email': 'a@example.com',
            'subject': 'Bug report', 'message': 'Something is broken.',
        })
        self.assertRedirects(response, reverse('feedback:contact'))
        self.assertEqual(Feedback.objects.count(), 1)

    def test_missing_message_is_rejected(self):
        response = self.client.post(reverse('feedback:contact'), {
            'name': 'Alice', 'email': 'a@example.com',
            'subject': 'Bug report', 'message': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.count(), 0)


class FeedbackListViewAccessTests(TestCase):
    def test_requires_admin(self):
        patient = make_patient()
        self.client.login(username=patient.user.username, password='test-pass-123')
        response = self.client.get(reverse('feedback:list'))
        self.assertNotEqual(response.status_code, 200)

    def test_admin_can_view(self):
        admin = make_admin()
        self.client.login(username=admin.username, password='test-pass-123')
        response = self.client.get(reverse('feedback:list'))
        self.assertEqual(response.status_code, 200)
