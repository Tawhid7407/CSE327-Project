from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import patient_required
from .models import MedicalHistory
from .forms import MedicalHistoryForm


@patient_required
def history_list(request):
    history = MedicalHistory.objects.filter(patient=request.user.patient_profile)
    return render(request, 'patient/medical_history.html', {'history': history})


@patient_required
def history_create(request):
    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.patient = request.user.patient_profile
            entry.save()
            messages.success(request, "Medical record added.")
            return redirect('medical_history:list')
    else:
        form = MedicalHistoryForm()
    return render(request, 'patient/medical_history_form.html', {'form': form, 'title': 'Add Record'})


@patient_required
def history_delete(request, pk):
    entry = get_object_or_404(MedicalHistory, pk=pk, patient=request.user.patient_profile)
    entry.delete()
    messages.success(request, "Record deleted.")
    return redirect('medical_history:list')
