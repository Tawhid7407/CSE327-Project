"""
Tests for the Department model and department views.
"""

from django.test import TestCase
from django.urls import reverse

from mediconnect.test_helpers import (
    make_admin,
    make_department,
    make_patient,
)

from .models import Department


class DepartmentModelTests(TestCase):

    def test_department_name_is_returned(self):
        department = make_department(name="Cardiology")

        self.assertEqual(
            str(department),
            "Cardiology"
        )

    def test_department_name_is_unique(self):
        make_department(name="Cardiology")

        with self.assertRaises(Exception):
            Department.objects.create(
                name="Cardiology"
            )


class DepartmentListViewAccessTests(TestCase):

    def setUp(self):
        self.url = reverse("departments:list")

    def test_logged_out_user_is_sent_to_login(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertIn(
            "/accounts/login/",
            response.url
        )

    def test_patient_cannot_view_department_list(self):
        patient = make_patient()

        self.client.login(
            username=patient.user.username,
            password="test-pass-123"
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertNotIn(
            "/accounts/login/",
            response.url
        )

    def test_admin_can_view_department_list(self):
        admin = make_admin()

        self.client.login(
            username=admin.username,
            password="test-pass-123"
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            200
        )


class DepartmentCreateViewTests(TestCase):

    def setUp(self):
        self.admin = make_admin()

        self.client.login(
            username=self.admin.username,
            password="test-pass-123"
        )

        self.url = reverse("departments:create")

    def test_valid_department_is_created(self):
        data = {
            "name": "Neurology",
            "description": "",
            "icon": "",
        }

        response = self.client.post(
            self.url,
            data
        )

        self.assertRedirects(
            response,
            reverse("departments:list")
        )

        self.assertTrue(
            Department.objects.filter(
                name="Neurology"
            ).exists()
        )

    def test_empty_name_is_not_allowed(self):
        data = {
            "name": "",
            "description": "",
            "icon": "",
        }

        response = self.client.post(
            self.url,
            data
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            Department.objects.count(),
            0
        )


class DepartmentDeleteViewTests(TestCase):

    def test_department_can_be_deleted(self):
        admin = make_admin()
        department = make_department()

        self.client.login(
            username=admin.username,
            password="test-pass-123"
        )

        response = self.client.post(
            reverse(
                "departments:delete",
                args=[department.pk]
            )
        )

        self.assertRedirects(
            response,
            reverse("departments:list")
        )

        self.assertFalse(
            Department.objects.filter(
                pk=department.pk
            ).exists()
        )