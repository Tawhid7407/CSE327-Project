"""
Unit tests for the departments app: the Department model and the
admin_required-protected CRUD views.
"""
from django.test import TestCase
from django.urls import reverse

from mediconnect.test_helpers import make_admin, make_department, make_patient
from .models import Department


class DepartmentModelTests(TestCase):
    def test_str_returns_name(self):
        dept = make_department(name="Cardiology")
        self.assertEqual(str(dept), "Cardiology")

    def test_name_must_be_unique(self):
        make_department(name="Cardiology")
        with self.assertRaises(Exception):
            Department.objects.create(name="Cardiology")


class DepartmentListViewAccessTests(TestCase):
    """Equivalence Partitioning on 'who is allowed in': anonymous, wrong
    role, admin."""

    def setUp(self):
        self.url = reverse('departments:list')

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_non_admin_user_is_redirected_away(self):
        patient = make_patient()
        self.client.login(username=patient.user.username, password='test-pass-123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('/accounts/login/', response.url)

    def test_admin_user_can_view(self):
        admin = make_admin()
        self.client.login(username=admin.username, password='test-pass-123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class DepartmentCreateViewTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.client.login(username=self.admin.username, password='test-pass-123')
        self.url = reverse('departments:create')

    def test_valid_name_creates_department(self):
        response = self.client.post(self.url, {
            'name': 'Neurology', 'description': '', 'icon': '',
        })
        self.assertRedirects(response, reverse('departments:list'))
        self.assertTrue(Department.objects.filter(name='Neurology').exists())

    def test_blank_name_is_rejected(self):
        response = self.client.post(self.url, {
            'name': '', 'description': '', 'icon': '',
        })
        self.assertEqual(response.status_code, 200)  # re-renders form
        self.assertEqual(Department.objects.count(), 0)


class DepartmentDeleteViewTests(TestCase):
    def test_delete_removes_department(self):
        admin = make_admin()
        dept = make_department()
        self.client.login(username=admin.username, password='test-pass-123')
        response = self.client.post(reverse('departments:delete', args=[dept.pk]))
        self.assertRedirects(response, reverse('departments:list'))
        self.assertFalse(Department.objects.filter(pk=dept.pk).exists())
