from django import forms
from .models import Prescription


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ('diagnosis', 'medicines', 'advice', 'follow_up_date')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medicines': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                                               'placeholder': 'e.g. Paracetamol 500mg - 3 times a day'}),
            'advice': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
