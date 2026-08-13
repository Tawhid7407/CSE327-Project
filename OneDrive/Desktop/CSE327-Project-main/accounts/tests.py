from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class LoginViewTests(TestCase):
    def test_patient_login_success(self):
        user = User.objects.create_user(
            username='patient1',
            email='patient1@example.com',
            password='StrongPass123',
            role='patient',
            is_approved=True,
        )

        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'patient1', 'password': 'StrongPass123'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user, user)

    def test_doctor_not_approved_cannot_login(self):
        User.objects.create_user(
            username='doctor1',
            email='doctor1@example.com',
            password='StrongPass123',
            role='doctor',
            is_approved=False,
        )

        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'doctor1', 'password': 'StrongPass123'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'Account not approved.')
