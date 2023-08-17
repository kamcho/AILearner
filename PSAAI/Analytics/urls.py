from .views import *
from . import views
from django.urls import path

urlpatterns = [
    path('<str:mail>/', OverallAnalytics.as_view(), name='overall-analytics'),
    path('<str:mail>/<str:subject>/Review', SubjectAnalytics.as_view(), name='subject-analysis'),



    ]