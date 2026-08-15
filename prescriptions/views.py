from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import doctor_required, patient_required
from appointments.models import Appointment
from .models import Prescription
from .forms import PrescriptionForm
from notifications.utils import create_notification


@doctor_required
def create_prescription(request, appointment_id):
    appt = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user.doctor_profile)
    if appt.status != 'completed':
        messages.warning(request, "Appointment must be marked completed first.")
        return redirect('appointments:manage')
    if hasattr(appt, 'prescription'):
        messages.info(request, "Prescription already exists.")
        return redirect('prescriptions:view', pk=appt.prescription.pk)

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            presc = form.save(commit=False)
            presc.appointment = appt
            presc.save()
            create_notification(
                appt.patient.user,
                f"Prescription issued by Dr. {request.user.get_full_name()}",
                link=f'/prescriptions/{presc.pk}/'
            )
            messages.success(request, "Prescription saved.")
            return redirect('appointments:manage')
    else:
        form = PrescriptionForm()
    return render(request, 'doctor/prescription_form.html', {'form': form, 'appointment': appt})


def prescription_detail(request, pk):
    presc = get_object_or_404(Prescription, pk=pk)
    # Access: only patient of that appointment, doctor, or admin
    user = request.user
    if not user.is_authenticated:
        return redirect('accounts:login')
    is_owner = (
        (user.role == 'patient' and presc.appointment.patient.user == user) or
        (user.role == 'doctor' and presc.appointment.doctor.user == user) or
        (user.role == 'admin' or user.is_superuser)
    )
    if not is_owner:
        messages.error(request, "Access denied.")
        return redirect('core:home')
    return render(request, 'patient/prescription_detail.html', {'prescription': presc})


@patient_required
def my_prescriptions(request):
    prescriptions = Prescription.objects.filter(
        appointment__patient=request.user.patient_profile
    ).select_related('appointment__doctor__user')
    return render(request, 'patient/my_prescriptions.html', {'prescriptions': prescriptions})
