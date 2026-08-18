from django.shortcuts import render

from doctors.models import DoctorProfile
from departments.models import Department


def home(request):

    top_doctors = DoctorProfile.objects.filter(
        user__is_approved=True,
        is_available=True
    ).select_related(
        "user",
        "department"
    )[:6]

    departments = Department.objects.all()[:8]

    context = {
        "top_doctors": top_doctors,
        "departments": departments,
    }

    return render(
        request,
        "core/home.html",
        context
    )


def about(request):
    return render(request, "core/about.html")