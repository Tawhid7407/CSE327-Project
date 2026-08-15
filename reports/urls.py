from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctors/', views.doctor_management, name='doctor_management'),
    path('doctors/<int:pk>/approve/', views.approve_doctor, name='approve_doctor'),
    path('doctors/<int:pk>/reject/', views.reject_doctor, name='reject_doctor'),
    path('doctors/<int:pk>/delete/', views.delete_doctor, name='delete_doctor'),
    path('patients/', views.patient_management, name='patient_management'),
    path('patients/<int:pk>/delete/', views.delete_patient, name='delete_patient'),
    path('reports/', views.reports_page, name='reports'),
]
