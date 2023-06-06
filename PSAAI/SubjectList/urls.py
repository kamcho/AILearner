from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('subject-selection/',Academia.as_view(),name='academia'),
    path('learn/',Learning.as_view(), name='learn'),
    path('learning/<str:pk>/', Read.as_view(), name='read'),

    ]