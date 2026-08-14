from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_reviewed', 'created_at')
    list_filter = ('is_reviewed',)
