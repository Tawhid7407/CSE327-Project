"""
Views for the MediConnect authentication module.
"""

from django.contrib import messages
from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import (
    RegisterForm,
    LoginForm,
    UserProfileForm,
    CustomPasswordChangeForm,
)


def register_view(request):
    """
    Register a new user account.
    """

    if request.user.is_authenticated:
        return redirect("accounts:role_redirect")

    form = RegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save()

        messages.success(
            request,
            "Registration successful. You can now log in.",
        )

        return redirect("accounts:login")

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def login_view(request):
    """
    Authenticate and log in a user.
    """

    if request.user.is_authenticated:
        return redirect("accounts:role_redirect")

    form = LoginForm(
        request,
        data=request.POST or None,
    )

    if form.is_valid():
        user = form.get_user()

        # Doctor approval is intentionally not checked here.
        # The authentication module should not depend on
        # the removed doctors app.

        login(request, user)

        messages.success(
            request,
            "Login successful.",
        )

        return redirect("accounts:role_redirect")

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    """
    Log out the currently authenticated user.
    """

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully.",
    )

    return redirect("accounts:login")


@login_required
def role_redirect(request):
    """
    Redirect authenticated users according to their role.

    This authentication-testing branch does not depend on
    the doctor, patient, core, or reports applications.
    """

    user = request.user

    if user.is_superuser or user.role == "admin":
        messages.info(
            request,
            "Admin authentication successful.",
        )
        return redirect("accounts:profile")

    if user.role == "doctor":
        messages.info(
            request,
            "Doctor authentication successful.",
        )
        return redirect("accounts:profile")

    if user.role == "patient":
        messages.info(
            request,
            "Patient authentication successful.",
        )
        return redirect("accounts:profile")

    return redirect("accounts:profile")


@login_required
def profile_view(request):
    """
    Display and update the authenticated user's profile.
    """

    form = UserProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    if form.is_valid():
        form.save()

        messages.success(
            request,
            "Profile updated successfully.",
        )

        return redirect("accounts:profile")

    return render(
        request,
        "accounts/profile.html",
        {"form": form},
    )


@login_required
def password_change_view(request):
    """
    Change the authenticated user's password.
    """

    form = CustomPasswordChangeForm(
        request.user,
        request.POST or None,
    )

    if form.is_valid():
        user = form.save()

        # Keep the user logged in after changing the password.
        update_session_auth_hash(request, user)

        messages.success(
            request,
            "Password changed successfully.",
        )

        return redirect("accounts:profile")

    return render(
        request,
        "accounts/password_change.html",
        {"form": form},
    )


class CustomPasswordResetView(PasswordResetView):
    """
    Password reset request view.
    """

    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy(
        "accounts:password_reset_done"
    )


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Password reset email sent confirmation.
    """

    template_name = "accounts/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Password reset confirmation view.
    """

    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy(
        "accounts:password_reset_complete"
    )


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Password reset completion view.
    """

    template_name = "accounts/password_reset_complete.html"