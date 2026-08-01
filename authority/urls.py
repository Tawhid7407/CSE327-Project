from django.urls import path
from . import views

app_name = 'authority'

urlpatterns = [
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # Admin dashboard / management / reports
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/doctors/', views.doctor_management, name='doctor_management'),
    path('admin-panel/doctors/<int:pk>/approve/', views.approve_doctor, name='approve_doctor'),
    path('admin-panel/doctors/<int:pk>/reject/', views.reject_doctor, name='reject_doctor'),
    path('admin-panel/doctors/<int:pk>/delete/', views.delete_doctor, name='delete_doctor'),
    path('admin-panel/patients/', views.patient_management, name='patient_management'),
    path('admin-panel/patients/<int:pk>/delete/', views.delete_patient, name='delete_patient'),
    path('admin-panel/reports/', views.reports_page, name='reports'),

    # Feedback inbox
    path('feedback/list/', views.feedback_list, name='feedback_list'),
]
