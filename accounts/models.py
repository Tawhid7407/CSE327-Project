from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_approved = models.BooleanField(default=True, help_text='Doctors need approval')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    def is_doctor(self):
        return self.role == 'doctor'

    def is_patient(self):
        return self.role == 'patient'

    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser



    

    
