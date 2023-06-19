from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('Exams/',Exams.as_view(),name='exams'),
    path('Exam-at/<str:pk>/<str:uuid>/Instructions', Start.as_view(), name='start'),
    path('Exam/<str:pk>/quizes/', Tests.as_view(), name='tests'),
    path('Exam/Finish', Finish.as_view(), name='finish'),
    path('Exam/<str:name>/Info', ExamSubjectDetail.as_view(), name='exam-subject-id'),
    path('Test/<str:uuid>/Revision/', TestDetail.as_view(), name='test-detail'),


    ]