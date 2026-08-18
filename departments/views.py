from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.decorators import admin_required
from .models import Department
from .forms import DepartmentForm


@admin_required
def department_list(request):

    departments = Department.objects.all()

    return render(
        request,
        "admin_panel/departments.html",
        {"departments": departments}
    )


@admin_required
def department_create(request):

    if request.method == "POST":
        form = DepartmentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Department created.")

            return redirect("departments:list")

    else:
        form = DepartmentForm()

    context = {
        "form": form,
        "title": "Add Department"
    }

    return render(
        request,
        "admin_panel/department_form.html",
        context
    )


@admin_required
def department_edit(request, pk):

    dept = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        form = DepartmentForm(
            request.POST,
            instance=dept
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Department updated.")

            return redirect("departments:list")

    else:
        form = DepartmentForm(instance=dept)

    context = {
        "form": form,
        "title": "Edit Department"
    }

    return render(
        request,
        "admin_panel/department_form.html",
        context
    )


@admin_required
def department_delete(request, pk):

    dept = get_object_or_404(
        Department,
        pk=pk
    )

    dept.delete()

    messages.success(
        request,
        "Department deleted."
    )

    return redirect("departments:list")