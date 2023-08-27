from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('subject-selection/', Academia.as_view(), name='academia'),
    path('learn/', Learning.as_view(), name='learn'),
    path('learning/<str:pk> /<str:name>/', Read.as_view(), name='read'),
    path('Assignments/', Assignment.as_view(), name='assignments'),
    path('<str:uuid>/Assignment-Lobby', AssignmentDetail.as_view(), name='assignment-lobby'),
    path('<str:uuid>/Take-Assessment/', TakeAssessment.as_view(), name='take-assessment'),
    path('<str:uuid>/Finish-Assessment/', FinishAssessment.as_view(), name='finish-assessment'),
    path('save/<str:pk> /<str:name>/progress', Finish.as_view(), name='save-progress'),
    path('<str:name>/syllabus-coverage/', Syllabus.as_view(), name='syllabus'),
    path('Notifications/', Messages.as_view(), name='notifications'),
    path('Progress/', MyProgress.as_view(), name='progress'),
    path('online-class/', UpcomingClasses.as_view(), name='upcoming-classes'),
    path('Video-Call', VideoCall.as_view(), name='video-call'),
    path('online-class/<str:id>/booking', ClassBookings.as_view(), name='book-class'),
    path('booked-classes/', BookedClasses.as_view(), name='booked-classes'),
    path('<str:id>/lobby', CallLobby.as_view(), name='lobby'),
    path('contact/', ContactUs.as_view(), name='contact')

]
