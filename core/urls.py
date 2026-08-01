from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home / about
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Accounts (auth)
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/redirect/', views.role_redirect, name='role_redirect'),
    path('accounts/profile/', views.profile_view, name='profile'),
    path('accounts/password-change/', views.password_change_view, name='password_change'),
    path('accounts/password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Appointments
    path('appointments/book/<int:doctor_id>/', views.book_appointment, name='book'),
    path('appointments/my/', views.my_appointments, name='my_appointments'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
    path('appointments/manage/', views.manage_appointments, name='manage'),
    path('appointments/<int:pk>/action/<str:action>/', views.appointment_action, name='action'),
    path('appointments/all/', views.all_appointments, name='all'),

    # Prescriptions
    path('prescriptions/create/<int:appointment_id>/', views.create_prescription, name='prescription_create'),
    path('prescriptions/<int:pk>/', views.prescription_detail, name='view'),
    path('prescriptions/my/', views.my_prescriptions, name='my'),

    # Medical history
    path('medical-history/', views.history_list, name='medical_history_list'),
    path('medical-history/add/', views.history_create, name='medical_history_create'),
    path('medical-history/<int:pk>/delete/', views.history_delete, name='medical_history_delete'),

    # Reviews
    path('reviews/submit/<int:doctor_id>/', views.submit_review, name='submit'),

    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_read, name='mark_read'),

    # Feedback (public contact form)
    path('feedback/contact/', views.contact_view, name='contact'),
]
