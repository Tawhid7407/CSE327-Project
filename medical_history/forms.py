from django import forms
from .models import MedicalHistory


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = ('condition', 'diagnosed_date', 'notes')
        widgets = {
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnosed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
