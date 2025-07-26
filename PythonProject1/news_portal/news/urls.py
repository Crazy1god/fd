from django.urls import path
from . import views

urlpatterns = [
    path('become_author/', views.become_author, name='become_author'),
]