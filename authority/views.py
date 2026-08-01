from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from core.decorators import admin_required
from core.models import User, Department, Appointment, Feedback
from core.utils import create_notification
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from .forms import DepartmentForm


# -------------------- Departments --------------------

@admin_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'admin_panel/departments.html', {'departments': departments})


@admin_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created.")
            return redirect('authority:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'admin_panel/department_form.html', {'form': form, 'title': 'Add Department'})


@admin_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated.")
            return redirect('authority:department_list')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'admin_panel/department_form.html', {'form': form, 'title': 'Edit Department'})


@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    dept.delete()
    messages.success(request, "Department deleted.")
    return redirect('authority:department_list')


# -------------------- Admin dashboard / reports --------------------

@admin_required
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_doctors': DoctorProfile.objects.count(),
        'approved_doctors': User.objects.filter(role='doctor', is_approved=True).count(),
        'pending_doctors': User.objects.filter(role='doctor', is_approved=False).count(),
        'total_patients': PatientProfile.objects.count(),
        'total_departments': Department.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'completed_appointments': Appointment.objects.filter(status='completed').count(),
        'total_feedback': Feedback.objects.count(),
        'recent_appointments': Appointment.objects.order_by('-created_at')[:5],
        'recent_feedback': Feedback.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def doctor_management(request):
    doctors = User.objects.filter(role='doctor').select_related('doctor_profile__department')
    status = request.GET.get('status', '')
    if status == 'pending':
        doctors = doctors.filter(is_approved=False)
    elif status == 'approved':
        doctors = doctors.filter(is_approved=True)
    return render(request, 'admin_panel/doctors.html', {'doctors': doctors, 'selected_status': status})


@admin_required
def approve_doctor(request, pk):
    user = get_object_or_404(User, pk=pk, role='doctor')
    user.is_approved = True
    user.save()
    create_notification(user, "Your doctor account has been approved. You can now log in.")
    messages.success(request, f"{user.username} approved.")
    return redirect('authority:doctor_management')


@admin_required
def reject_doctor(request, pk):
    user = get_object_or_404(User, pk=pk, role='doctor')
    username = user.username
    user.delete()
    messages.success(request, f"{username} rejected and removed.")
    return redirect('authority:doctor_management')


@admin_required
def delete_doctor(request, pk):
    user = get_object_or_404(User, pk=pk, role='doctor')
    username = user.username
    user.delete()
    messages.success(request, f"Doctor {username} deleted.")
    return redirect('authority:doctor_management')


@admin_required
def patient_management(request):
    patients = User.objects.filter(role='patient')
    return render(request, 'admin_panel/patients.html', {'patients': patients})


@admin_required
def delete_patient(request, pk):
    user = get_object_or_404(User, pk=pk, role='patient')
    username = user.username
    user.delete()
    messages.success(request, f"Patient {username} deleted.")
    return redirect('authority:patient_management')


@admin_required
def reports_page(request):
    # Doctor per department
    dept_stats = Department.objects.annotate(doctor_count=Count('doctorprofile'))
    # Appointment status breakdown
    status_stats = Appointment.objects.values('status').annotate(count=Count('id'))
    context = {
        'dept_stats': dept_stats,
        'status_stats': status_stats,
        'total_users': User.objects.count(),
        'total_doctors': DoctorProfile.objects.count(),
        'total_patients': PatientProfile.objects.count(),
        'total_appointments': Appointment.objects.count(),
    }
    return render(request, 'admin_panel/reports.html', context)


# -------------------- Feedback inbox --------------------

@admin_required
def feedback_list(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'admin_panel/feedback.html', {'feedbacks': feedbacks})
