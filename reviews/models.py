from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from doctors.models import DoctorProfile
from patients.models import PatientProfile


class Review(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('doctor', 'patient')

    def __str__(self):
        return f"{self.patient} rated {self.doctor} {self.rating} stars"
