from django import forms
from django.utils import timezone
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('appointment_date', 'appointment_time', 'reason')
        widgets = {
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                            'placeholder': 'Describe your symptoms or reason for visit...'}),
        }

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date < timezone.localdate():
            raise forms.ValidationError("Cannot book appointment in the past.")
        return date

