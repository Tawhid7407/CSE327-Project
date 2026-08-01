from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib import messages
from django.urls import reverse_lazy
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from .decorators import patient_required, doctor_required, admin_required
from .forms import (
    RegisterForm, LoginForm, UserProfileForm, CustomPasswordChangeForm,
    AppointmentForm, PrescriptionForm, MedicalHistoryForm, ReviewForm, FeedbackForm,
)
from .models import Department, Appointment, Prescription, MedicalHistory, Review, Notification, Feedback
from .utils import create_notification


# -------------------- Home / about --------------------

def home(request):
    top_doctors = DoctorProfile.objects.filter(
        user__is_approved=True, is_available=True
    ).select_related('user', 'department')[:6]
    departments = Department.objects.all()[:8]
    return render(request, 'core/home.html', {
        'top_doctors': top_doctors,
        'departments': departments,
    })


def about(request):
    return render(request, 'core/about.html')


# -------------------- Accounts (auth) --------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:role_redirect')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-create profile
            if user.role == 'patient':
                PatientProfile.objects.create(user=user)
                messages.success(request, "Registration successful! You can now log in.")
            else:  # doctor
                DoctorProfile.objects.create(user=user)
                messages.info(request, "Registration submitted! Awaiting admin approval before you can log in.")
            return redirect('core:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:role_redirect')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.role == 'doctor' and not user.is_approved:
                messages.error(request, "Your account is awaiting admin approval.")
                return redirect('core:login')
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('core:role_redirect')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('core:home')


@login_required
def role_redirect(request):
    """Redirect user to their role-specific dashboard."""
    user = request.user
    if user.is_superuser or user.role == 'admin':
        return redirect('authority:admin_dashboard')
    elif user.role == 'doctor':
        return redirect('doctors:dashboard')
    elif user.role == 'patient':
        return redirect('patients:dashboard')
    return redirect('core:home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('core:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})


# Password reset views (email link based)
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('core:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('core:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


# -------------------- Appointments --------------------

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
            create_notification(
                doctor.user,
                f"New appointment request from {request.user.get_full_name() or request.user.username}",
                link='/doctor/appointments/manage/'
            )
            messages.success(request, "Appointment request submitted!")
            return redirect('core:my_appointments')
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
    return redirect('core:my_appointments')


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
        return redirect('core:manage')
    appt.status = valid[action]
    appt.save()
    create_notification(
        appt.patient.user,
        f"Your appointment on {appt.appointment_date} has been {valid[action]}."
    )
    messages.success(request, f"Appointment {valid[action]}.")
    return redirect('core:manage')


@admin_required
def all_appointments(request):
    appointments = Appointment.objects.all().select_related('patient__user', 'doctor__user')
    return render(request, 'admin_panel/appointments.html', {'appointments': appointments})


# -------------------- Prescriptions --------------------

@doctor_required
def create_prescription(request, appointment_id):
    appt = get_object_or_404(Appointment, pk=appointment_id, doctor=request.user.doctor_profile)
    if appt.status != 'completed':
        messages.warning(request, "Appointment must be marked completed first.")
        return redirect('core:manage')
    if hasattr(appt, 'prescription'):
        messages.info(request, "Prescription already exists.")
        return redirect('core:view', pk=appt.prescription.pk)

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
            return redirect('core:manage')
    else:
        form = PrescriptionForm()
    return render(request, 'doctor/prescription_form.html', {'form': form, 'appointment': appt})


def prescription_detail(request, pk):
    presc = get_object_or_404(Prescription, pk=pk)
    # Access: only patient of that appointment, doctor, or admin
    user = request.user
    if not user.is_authenticated:
        return redirect('core:login')
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


# -------------------- Medical history --------------------

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
            return redirect('core:medical_history_list')
    else:
        form = MedicalHistoryForm()
    return render(request, 'patient/medical_history_form.html', {'form': form, 'title': 'Add Record'})


@patient_required
def history_delete(request, pk):
    entry = get_object_or_404(MedicalHistory, pk=pk, patient=request.user.patient_profile)
    entry.delete()
    messages.success(request, "Record deleted.")
    return redirect('core:medical_history_list')


# -------------------- Reviews --------------------

@patient_required
def submit_review(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    patient = request.user.patient_profile

    # Only allow review if patient has a completed appointment with this doctor
    has_completed = Appointment.objects.filter(
        patient=patient, doctor=doctor, status='completed'
    ).exists()
    if not has_completed:
        messages.error(request, "You can only review doctors after a completed appointment.")
        return redirect('doctors:detail', pk=doctor_id)

    existing = Review.objects.filter(doctor=doctor, patient=patient).first()
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = doctor
            review.patient = patient
            review.save()
            messages.success(request, "Review submitted. Thank you!")
            return redirect('doctors:detail', pk=doctor_id)
    else:
        form = ReviewForm(instance=existing)
    return render(request, 'patient/review_form.html', {'form': form, 'doctor': doctor})


# -------------------- Notifications --------------------

@login_required
def notification_list(request):
    notifications = request.user.notifications.all()
    # Mark all as read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'includes/notifications.html', {'notifications': notifications})


@login_required
def mark_read(request, pk):
    n = get_object_or_404(Notification, pk=pk, user=request.user)
    n.is_read = True
    n.save()
    if n.link:
        return redirect(n.link)
    return redirect('core:notification_list')


# -------------------- Feedback (public contact form) --------------------

def contact_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect('core:contact')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = FeedbackForm(initial=initial)
    return render(request, 'core/contact.html', {'form': form})
