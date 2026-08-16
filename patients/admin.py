from django.contrib import admin
from .models import PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'blood_group')
    list_filter = ('gender', 'blood_group')
    search_fields = ('user__username', 'user__first_name')


/new