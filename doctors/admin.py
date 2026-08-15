from django.contrib import admin
from .models import DoctorProfile, Availability


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    
    list_display = ('user', 'department', 'specialization', 'consultation_fee', 'is_available')
    
    list_filter = ('department', 'is_available')
    
    search_fields = ('user__username', 'user__first_name', 'specialization')




@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    
    list_display = ('doctor', 'day', 'start_time', 'end_time')
    
    list_filter = ('day',)
