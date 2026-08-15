"""Unit tests for the core app: the public home and about pages."""
from django.test import TestCase
from django.urls import reverse

from mediconnect.test_helpers import make_department, make_doctor


class HomeViewTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_lists_available_departments(self):
        make_department(name="Cardiology")
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, "Cardiology")

    def test_home_page_shows_only_approved_available_doctors(self):
        make_doctor(username='approved_doc', last_name='Available', approved=True)
        make_doctor(username='unapproved_doc', last_name='Hidden', approved=False)
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, "Available")
        self.assertNotContains(response, "Hidden")


class AboutViewTests(TestCase):
    def test_about_page_loads(self):
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
