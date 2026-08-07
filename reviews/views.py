from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import patient_required
from doctors.models import DoctorProfile
from appointments.models import Appointment
from .models import Review
from .forms import ReviewForm


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
