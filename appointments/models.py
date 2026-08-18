from django.db import models
from doctors.models import DoctorProfile
from patients.models import PatientProfile


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(help_text='Brief description of your symptoms/reason')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f"{self.patient} → {self.doctor} on {self.appointment_date}"

    @property
    def status_badge(self):
        return {
            'pending': 'warning',
            'approved': 'primary',
            'rejected': 'danger',
            'completed': 'success',
            'cancelled': 'secondary',
        }.get(self.status, 'secondary')

