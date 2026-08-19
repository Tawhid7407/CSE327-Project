from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import patient_required, doctor_required, admin_required
from doctors.models import DoctorProfile
from .models import Appointment
from .forms import AppointmentForm
from notifications.utils import create_notification


@patient_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id, user__is_approved=True)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = request.user.patient_profile
            appt.doctor = doctor
            appt.save()
            # Notify doctor
            create_notification(
                doctor.user,
                f"New appointment request from {request.user.get_full_name() or request.user.username}",
                link='/doctor/appointments/manage/'
            )
            messages.success(request, "Appointment request submitted!")
            return redirect('appointments:my_appointments')
    else:
        form = AppointmentForm()
    return render(request, 'patient/book_appointment.html', {'form': form, 'doctor': doctor})


@patient_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user.patient_profile).select_related('doctor__user')
    return render(request, 'patient/my_appointments.html', {'appointments': appointments})


@patient_required
def cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient=request.user.patient_profile)
    if appt.status in ('pending', 'approved'):
        appt.status = 'cancelled'
        appt.save()
        create_notification(appt.doctor.user, f"Appointment cancelled by {appt.patient}")
        messages.success(request, "Appointment cancelled.")
    else:
        messages.error(request, "Cannot cancel this appointment.")
    return redirect('appointments:my_appointments')


@doctor_required
def manage_appointments(request):
    doctor = request.user.doctor_profile
    status = request.GET.get('status', '')
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient__user')
    if status:
        appointments = appointments.filter(status=status)
    return render(request, 'doctor/appointments.html', {
        'appointments': appointments,
        'selected_status': status,
    })


@doctor_required
def appointment_action(request, pk, action):
    appt = get_object_or_404(Appointment, pk=pk, doctor=request.user.doctor_profile)
    valid = {'approve': 'approved', 'reject': 'rejected', 'complete': 'completed'}
    if action not in valid:
        messages.error(request, "Invalid action.")
        return redirect('appointments:manage')
    appt.status = valid[action]
    appt.save()
    create_notification(
        appt.patient.user,
        f"Your appointment on {appt.appointment_date} has been {valid[action]}."
    )
    messages.success(request, f"Appointment {valid[action]}.")
    return redirect('appointments:manage')


@admin_required
def all_appointments(request):
    appointments = Appointment.objects.all().select_related('patient__user', 'doctor__user')
    return render(request, 'admin_panel/appointments.html', {'appointments': appointments})
    
