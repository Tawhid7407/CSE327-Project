from django.contrib import admin
from .models import MedicalHistory


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'condition', 'diagnosed_date')
    search_fields = ('condition',)
