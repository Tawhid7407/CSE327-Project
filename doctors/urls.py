

from django.urls import path

from . import views

app_name = 'doctors'


urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('availability/', views.availability_view, name='availability'),
    path('availability/<int:pk>/delete/', views.availability_delete, name='availability_delete'),
    path('reviews/', views.my_reviews, name='my_reviews'),
    path('list/', views.doctor_list, name='list'),
    path('<int:pk>/', views.doctor_detail, name='detail'),
]
