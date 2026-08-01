from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('', views.department_list, name='list'),
    path('create/', views.department_create, name='create'),
    path('<int:pk>/edit/', views.department_edit, name='edit'),
    path('<int:pk>/delete/', views.department_delete, name='delete'),
]
