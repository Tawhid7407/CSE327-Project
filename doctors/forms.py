from django import forms
from .models import DoctorProfile, Availability


class DoctorProfileForm(forms.ModelForm):
    class Meta:

        model = DoctorProfile
        fields = ('department', 'specialization', 'qualification', 'experience_years', 'consultation_fee', 'bio', 'is_available')
        widgets = {

            'department': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MBBS, MD, etc.'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AvailabilityForm(forms.ModelForm):
    class Meta:

        model = Availability
        fields = ('day', 'start_time', 'end_time')
        widgets = {
            'day': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean(self):
        
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned
