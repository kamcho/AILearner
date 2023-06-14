from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('subject-selection/', Academia.as_view(), name='academia'),
    path('learn/', Learning.as_view(), name='learn'),
    path('learning/<str:pk>/', Read.as_view(), name='read'),
    path('save/<str:name>/progress', Finish.as_view(), name='finish'),
    path('<str:name>/syllabus-coverage/', Syllabus.as_view(), name='syllabus'),
    path('Notifications/', Messages.as_view(), name='notifications'),

]
