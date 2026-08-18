"""Tests for the feedback app."""

from django.test import TestCase
from django.urls import reverse

from mediconnect.test_helpers import make_admin, make_patient
from .models import Feedback


class FeedbackModelTests(TestCase):

    def test_str_method(self):
        feedback = Feedback.objects.create(
            name="Alice",
            email="a@example.com",
            subject="Bug report",
            message="Something is broken."
        )

        self.assertEqual(str(feedback), "Bug report - Alice")


class ContactViewTests(TestCase):

    def test_feedback_can_be_submitted(self):
        data = {
            "name": "Alice",
            "email": "a@example.com",
            "subject": "Bug report",
            "message": "Something is broken."
        }

        response = self.client.post(
            reverse("feedback:contact"),
            data
        )

        self.assertRedirects(
            response,
            reverse("feedback:contact")
        )
        self.assertEqual(Feedback.objects.count(), 1)

    def test_message_cannot_be_empty(self):
        data = {
            "name": "Alice",
            "email": "a@example.com",
            "subject": "Bug report",
            "message": ""
        }

        response = self.client.post(
            reverse("feedback:contact"),
            data
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.count(), 0)


class FeedbackListViewAccessTests(TestCase):

    def test_normal_user_cannot_access_feedback_list(self):
        patient = make_patient()

        self.client.login(
            username=patient.user.username,
            password="test-pass-123"
        )

        response = self.client.get(
            reverse("feedback:list")
        )

        self.assertNotEqual(response.status_code, 200)

    def test_admin_can_access_feedback_list(self):
        admin = make_admin()

        self.client.login(
            username=admin.username,
            password="test-pass-123"
        )

        response = self.client.get(
            reverse("feedback:list")
        )

        self.assertEqual(response.status_code, 200)