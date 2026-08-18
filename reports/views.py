from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count

from accounts.decorators import admin_required
from accounts.models import User
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from departments.models import Department
from appointments.models import Appointment
from feedback.models import Feedback


@admin_required
def admin_dashboard(request):

    total_users = User.objects.count()
    total_doctors = DoctorProfile.objects.count()
    total_patients = PatientProfile.objects.count()
    total_departments = Department.objects.count()
    total_appointments = Appointment.objects.count()
    total_feedback = Feedback.objects.count()

    approved_doctors = User.objects.filter(
        role="doctor",
        is_approved=True
    ).count()

    pending_doctors = User.objects.filter(
        role="doctor",
        is_approved=False
    ).count()

    pending_appointments = Appointment.objects.filter(
        status="pending"
    ).count()

    completed_appointments = Appointment.objects.filter(
        status="completed"
    ).count()

    recent_appointments = Appointment.objects.order_by(
        "-created_at"
    )[:5]

    recent_feedback = Feedback.objects.order_by(
        "-created_at"
    )[:5]

    context = {
        "total_users": total_users,
        "total_doctors": total_doctors,
        "approved_doctors": approved_doctors,
        "pending_doctors": pending_doctors,
        "total_patients": total_patients,
        "total_departments": total_departments,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "completed_appointments": completed_appointments,
        "total_feedback": total_feedback,
        "recent_appointments": recent_appointments,
        "recent_feedback": recent_feedback,
    }

    return render(
        request,
        "admin_panel/dashboard.html",
        context
    )


@admin_required
def doctor_management(request):

    doctors = User.objects.filter(
        role="doctor"
    ).select_related(
        "doctor_profile__department"
    )

    status = request.GET.get("status", "")

    if status == "pending":
        doctors = doctors.filter(is_approved=False)

    elif status == "approved":
        doctors = doctors.filter(is_approved=True)

    context = {
        "doctors": doctors,
        "selected_status": status,
    }

    return render(
        request,
        "admin_panel/doctors.html",
        context
    )


@admin_required
def approve_doctor(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
        role="doctor"
    )

    user.is_approved = True
    user.save()

    from notifications.utils import create_notification

    create_notification(
        user,
        "Your doctor account has been approved. You can now log in."
    )

    messages.success(
        request,
        f"{user.username} approved."
    )

    return redirect("reports:doctor_management")


@admin_required
def reject_doctor(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
        role="doctor"
    )

    username = user.username
    user.delete()

    messages.success(
        request,
        f"{username} rejected and removed."
    )

    return redirect("reports:doctor_management")


@admin_required
def delete_doctor(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
        role="doctor"
    )

    username = user.username
    user.delete()

    messages.success(
        request,
        f"Doctor {username} deleted."
    )

    return redirect("reports:doctor_management")


@admin_required
def patient_management(request):

    patients = User.objects.filter(role="patient")

    return render(
        request,
        "admin_panel/patients.html",
        {"patients": patients}
    )


@admin_required
def delete_patient(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
        role="patient"
    )

    username = user.username
    user.delete()

    messages.success(
        request,
        f"Patient {username} deleted."
    )

    return redirect("reports:patient_management")


@admin_required
def reports_page(request):

    dept_stats = Department.objects.annotate(
        doctor_count=Count("doctorprofile")
    )

    status_stats = Appointment.objects.values(
        "status"
    ).annotate(
        count=Count("id")
    )

    context = {
        "dept_stats": dept_stats,
        "status_stats": status_stats,
        "total_users": User.objects.count(),
        "total_doctors": DoctorProfile.objects.count(),
        "total_patients": PatientProfile.objects.count(),
        "total_appointments": Appointment.objects.count(),
    }

    return render(
        request,
        "admin_panel/reports.html",
        context
    )