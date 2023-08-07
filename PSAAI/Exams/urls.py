from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [

    path('', Exams.as_view(),name='exams'),
    path('<str:pk>/<str:uuid>/Instructions', Start.as_view(), name='start'),
    path('<str:uuid>/quizes/', Tests.as_view(), name='tests'),
    path('<str:uuid>/Finish', Finish.as_view(), name='finish'),

    path('<str:subject>/<str:topic>/Info', ExamSubjectDetail.as_view(), name='exam-subject-id'),
    path('<str:subject>/TopicInfo', ExamTopicView.as_view(), name='exam-topic-id'),
    path('<str:subject>/set-test/', SetTest.as_view(), name='set-test'),
    path('<str:subject>/<str:uuid>/', StartRepeat.as_view(), name='retake'),
    path('Test/<str:uuid>/Revision/', TestDetail.as_view(), name='test-detail'),


    ]