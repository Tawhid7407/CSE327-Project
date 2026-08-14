from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import RegisterForm, LoginForm, UserProfileForm, CustomPasswordChangeForm
from doctors.models import DoctorProfile
from patients.models import PatientProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()

        if user.role == 'patient':
            PatientProfile.objects.create(user=user)
        else:
            DoctorProfile.objects.create(user=user)

        messages.success(request, 'Registration successful.')
        return redirect('accounts:login')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    form = LoginForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()

        if user.role == 'doctor' and not user.is_approved:
            messages.error(request, 'Account not approved.')
            return redirect('accounts:login')

        login(request, user)
        return redirect('accounts:role_redirect')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('core:home')


@login_required
def role_redirect(request):
    user = request.user

    if user.is_superuser or user.role == 'admin':
        return redirect('reports:admin_dashboard')
    if user.role == 'doctor':
        return redirect('doctors:dashboard')
    if user.role == 'patient':
        return redirect('patients:dashboard')

    return redirect('core:home')


@login_required
def profile_view(request):
    form = UserProfileForm(request.POST or None, request.FILES or None,
                           instance=request.user)

    if form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def password_change_view(request):
    form = CustomPasswordChangeForm(request.user, request.POST or None)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed.')
        return redirect('accounts:profile')

    return render(request, 'accounts/password_change.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'