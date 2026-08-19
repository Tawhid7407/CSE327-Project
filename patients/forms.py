from django import forms
from .models import PatientProfile


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ('age', 'gender', 'blood_group', 'address')
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), //
        }
