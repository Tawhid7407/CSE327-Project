from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def patient_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'patient':
            messages.error(request, "Access denied. Patient account required.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def doctor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'doctor':
            messages.error(request, "Access denied. Doctor account required.")
            return redirect('core:home')
        if not request.user.is_approved:
            messages.warning(request, "Your doctor account is awaiting admin approval.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'admin' and not request.user.is_superuser:
            messages.error(request, "Access denied. Admin account required.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper
