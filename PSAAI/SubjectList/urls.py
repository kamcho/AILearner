from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('Grade-<str:grade>/Subjects/', Learning.as_view(), name='learn'),
    path('learning/<str:topic> /<str:subtopic>/', Read.as_view(), name='read'),
    path('Assignments/', Assignment.as_view(), name='assignments'),
    path('<str:uuid>/Assignment-Lobby', AssignmentDetail.as_view(), name='assignment-lobby'),

    path('save/<str:topic> /<str:subtopic>/Save-Progress/', Finish.as_view(), name='save-progress'),
    path('<str:subject_id>/syllabus-coverage/', Syllabus.as_view(), name='syllabus'),
    path('Notifications/', Messages.as_view(), name='notifications'),
    path('Grade-<str:grade>/Learning-Progress', MyProgress.as_view(), name='progress'),

    path('contact/', ContactUs.as_view(), name='contact')

]
