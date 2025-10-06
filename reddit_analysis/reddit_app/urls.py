from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/stats/', views.get_stats, name='stats'),
    path('api/test-es/', views.test_elasticsearch, name='test_es'),  # Nouvelle route
]