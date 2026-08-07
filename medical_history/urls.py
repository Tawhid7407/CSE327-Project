from django.urls import path
from . import views

app_name = 'medical_history'

urlpatterns = [
    path('', views.history_list, name='list'),
    path('add/', views.history_create, name='create'),
    path('<int:pk>/delete/', views.history_delete, name='delete'),
]
