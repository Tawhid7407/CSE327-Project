from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from core.decorators import doctor_required
from .models import DoctorProfile, Availability
from .forms import DoctorProfileForm, AvailabilityForm
from core.models import Appointment, Review


@doctor_required
def dashboard(request):
    doctor = request.user.doctor_profile
    appointments = Appointment.objects.filter(doctor=doctor)
    context = {
        'doctor': doctor,
        'total_appointments': appointments.count(),
        'pending_count': appointments.filter(status='pending').count(),
        'approved_count': appointments.filter(status='approved').count(),
        'completed_count': appointments.filter(status='completed').count(),
        'recent_appointments': appointments.order_by('-created_at')[:5],
        'avg_rating': doctor.average_rating,
        'total_reviews': doctor.total_reviews,
    }
    return render(request, 'doctor/dashboard.html', context)


@doctor_required
def edit_profile(request):
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('doctors:dashboard')
    else:
        form = DoctorProfileForm(instance=doctor)
    return render(request, 'doctor/edit_profile.html', {'form': form})


@doctor_required
def availability_view(request):
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = doctor
            try:
                slot.save()
                messages.success(request, "Availability slot added.")
            except Exception:
                messages.error(request, "This time slot already exists.")
            return redirect('doctors:availability')
    else:
        form = AvailabilityForm()
    slots = doctor.availabilities.all()
    return render(request, 'doctor/availability.html', {'form': form, 'slots': slots})


@doctor_required
def availability_delete(request, pk):
    slot = get_object_or_404(Availability, pk=pk, doctor=request.user.doctor_profile)
    slot.delete()
    messages.success(request, "Slot removed.")
    return redirect('doctors:availability')


@doctor_required
def my_reviews(request):
    doctor = request.user.doctor_profile
    reviews = doctor.reviews.select_related('patient__user').order_by('-created_at')
    return render(request, 'doctor/reviews.html', {'reviews': reviews, 'doctor': doctor})


# Public: browse doctors (patients & guests)
def doctor_list(request):
    doctors = DoctorProfile.objects.filter(user__is_approved=True, is_available=True).select_related('user', 'department')
    query = request.GET.get('q', '')
    dept_id = request.GET.get('department', '')
    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialization__icontains=query)
        )
    if dept_id:
        doctors = doctors.filter(department_id=dept_id)

    from core.models import Department
    departments = Department.objects.all()
    return render(request, 'patient/doctor_list.html', {
        'doctors': doctors,
        'departments': departments,
        'query': query,
        'selected_dept': dept_id,
    })


def doctor_detail(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    availabilities = doctor.availabilities.all()
    reviews = doctor.reviews.select_related('patient__user').order_by('-created_at')[:10]
    return render(request, 'patient/doctor_detail.html', {
        'doctor': doctor,
        'availabilities': availabilities,
        'reviews': reviews,
    })
