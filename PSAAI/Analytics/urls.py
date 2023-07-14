from .views import *
from . import views
from django.urls import path

urlpatterns = [
    path('', OverallAnalytics.as_view(), name='overall-analytics')



    ]