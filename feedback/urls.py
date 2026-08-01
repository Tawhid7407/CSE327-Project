from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('list/', views.feedback_list, name='list'),
]
