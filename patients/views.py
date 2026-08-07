from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.decorators import patient_required
from .forms import PatientProfileForm
from appointments.models import Appointment
from prescriptions.models import Prescription


@patient_required
def dashboard(request):
    patient = request.user.patient_profile
    appointments = Appointment.objects.filter(patient=patient)
    prescriptions = Prescription.objects.filter(appointment__patient=patient)
    context = {
        'patient': patient,
        'total_appointments': appointments.count(),
        'upcoming_count': appointments.filter(status__in=['pending', 'approved']).count(),
        'completed_count': appointments.filter(status='completed').count(),
        'total_prescriptions': prescriptions.count(),
        'recent_appointments': appointments.order_by('-created_at')[:5],
    }
    return render(request, 'patient/dashboard.html', context)


@patient_required
def edit_profile(request):
    patient = request.user.patient_profile
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('patients:dashboard')
    else:
        form = PatientProfileForm(instance=patient)
    return render(request, 'patient/edit_profile.html', {'form': form})
