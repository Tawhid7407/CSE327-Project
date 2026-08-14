"""
Unit tests for the notifications app: the create_notification() utility,
the global unread_notifications context processor (3 equivalence classes:
anonymous / authenticated with unread / authenticated without unread),
and the notification_list view marking notifications as read.
"""
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from mediconnect.test_helpers import make_patient
from .context_processors import unread_notifications
from .models import Notification
from .utils import create_notification


class CreateNotificationTests(TestCase):
    def test_creates_notification_with_given_fields(self):
        patient = make_patient()
        note = create_notification(patient.user, "Hello!", link="/x/")
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(note.user, patient.user)
        self.assertEqual(note.message, "Hello!")
        self.assertEqual(note.link, "/x/")
        self.assertFalse(note.is_read)


class UnreadNotificationsContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_anonymous_user_gets_zero_count(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        ctx = unread_notifications(request)
        self.assertEqual(ctx['unread_notifications_count'], 0)

    def test_authenticated_user_with_no_unread_gets_zero(self):
        patient = make_patient()
        request = self.factory.get('/')
        request.user = patient.user
        ctx = unread_notifications(request)
        self.assertEqual(ctx['unread_notifications_count'], 0)

    def test_authenticated_user_with_unread_gets_correct_count(self):
        patient = make_patient()
        create_notification(patient.user, "One")
        create_notification(patient.user, "Two")
        request = self.factory.get('/')
        request.user = patient.user
        ctx = unread_notifications(request)
        self.assertEqual(ctx['unread_notifications_count'], 2)


class NotificationListViewTests(TestCase):
    def test_viewing_the_list_marks_all_as_read(self):
        patient = make_patient()
        create_notification(patient.user, "One")
        create_notification(patient.user, "Two")
        self.client.login(username=patient.user.username, password='test-pass-123')
        self.client.get(reverse('notifications:list'))
        self.assertEqual(
            Notification.objects.filter(user=patient.user, is_read=False).count(), 0
        )
