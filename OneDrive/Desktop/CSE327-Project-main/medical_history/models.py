from django.db import models
from patients.models import PatientProfile


class MedicalHistory(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='history')
    condition = models.CharField(max_length=200)
    diagnosed_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-diagnosed_date']

    def __str__(self):
        return f"{self.patient} - {self.condition}"
