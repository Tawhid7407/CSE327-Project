"""

Unit tests for the doctors app
updated code 

"""
from django.test import TestCase
from django.urls import reverse

from mediconnect.test_helpers import make_department, make_doctor, make_patient
from reviews.models import Review


class DoctorAverageRatingTests(TestCase):
    """Equivalence classes: no reviews vs. one or more reviews."""

    def setUp(self):
        self.doctor = make_doctor()

    def test_average_rating_with_no_reviews_is_zero(self):
        self.assertEqual(self.doctor.average_rating, 0)
        self.assertEqual(self.doctor.total_reviews, 0)

    def test_average_rating_with_reviews_is_the_mean(self):
        p1 = make_patient(username='p1')
        p2 = make_patient(username='p2')
        Review.objects.create(doctor=self.doctor, patient=p1, rating=4)
        Review.objects.create(doctor=self.doctor, patient=p2, rating=2)
        self.assertEqual(self.doctor.average_rating, 3.0)
        self.assertEqual(self.doctor.total_reviews, 2)


class DoctorListViewTests(TestCase):
    def setUp(self):
        self.dept = make_department(name="Cardiology")
        self.doctor = make_doctor(
            username='drsmith', first_name='John', last_name='Smith',
            department=self.dept,
        )

    def test_matching_query_returns_doctor(self):
        response = self.client.get(reverse('doctors:list'), {'q': 'Smith'})
        self.assertContains(response, 'Smith')

    def test_non_matching_query_returns_no_doctor(self):
        response = self.client.get(reverse('doctors:list'), {'q': 'Nobody'})
        self.assertNotContains(response, 'Smith')

    def test_department_filter(self):
        other_dept = make_department(name="Neurology")
        response = self.client.get(reverse('doctors:list'), {'department': other_dept.pk})
        self.assertNotContains(response, 'Smith')


class DoctorDetailViewTests(TestCase):
    def test_detail_page_loads(self):
        doctor = make_doctor()
        response = self.client.get(reverse('doctors:detail', args=[doctor.pk]))
        self.assertEqual(response.status_code, 200)
