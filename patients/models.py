from django.db import models
from django.conf import settings


class PatientProfile(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))
    BLOOD_GROUPS = (
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
