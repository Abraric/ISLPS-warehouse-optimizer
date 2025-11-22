"""
URL routing for ML service endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('predict-location/', views.predict_location, name='predict_location'),
]

