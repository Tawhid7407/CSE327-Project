from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/<int:doctor_id>/', views.book_appointment, name='book'),
    path('my/', views.my_appointments, name='my_appointments'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
    path('manage/', views.manage_appointments, name='manage'),
    path('<int:pk>/action/<str:action>/', views.appointment_action, name='action'),
    path('all/', views.all_appointments, name='all'),
]
