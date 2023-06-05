from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('Exams/',Exams.as_view(),name='exams'),
    path('Exam-at/<str:name>/year', ExamCourseList.as_view(), name='exam-list')


    ]