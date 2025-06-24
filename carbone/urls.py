from django.urls import path
from . import views
from .views import dashboard_carbone

urlpatterns = [
    path('dashboard/', views.dashboard_carbone, name='dashboard_carbone'),
    path('dashboard/', dashboard_carbone, name='carbone_dashboard'),
]
