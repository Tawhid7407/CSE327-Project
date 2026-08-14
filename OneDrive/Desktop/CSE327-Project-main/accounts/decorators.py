from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def patient_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.role != 'patient':
            messages.error(request, 'Patient account required.')
            return redirect('core:home')

        return view_func(request, *args, **kwargs)

    return wrapper


def doctor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.role != 'doctor':
            messages.error(request, 'Doctor account required.')
            return redirect('core:home')

        if not request.user.is_approved:
            messages.warning(request, 'Doctor account is awaiting approval.')
            return redirect('core:home')

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        if request.user.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Admin account required.')
            return redirect('core:home')

        return view_func(request, *args, **kwargs)

    return wrapper