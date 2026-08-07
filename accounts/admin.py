from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the MediConnect User model.
    """

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_approved',
        'is_active',
        'created_at',
    )

    list_filter = (
        'role',
        'is_approved',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone',
    )

    ordering = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'MediConnect Information',
            {
                'fields': (
                    'role',
                    'phone',
                    'profile_pic',
                    'is_approved',
                    'created_at',
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'MediConnect Information',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'role',
                    'phone',
                    'profile_pic',
                    'is_approved',
                ),
            },
        ),
    )

    readonly_fields = ('created_at',)