from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('My-Kids/', MyKidsView.as_view(), name='my-kids'),
    path('Home/', GuardianHome.as_view(), name='guardian-home'),
    path('Learner/<str:email>/', TaskSelection.as_view(), name='task-view-select'),
    path('Guardian/<str:email>/test-/quiz/', KidTests.as_view(), name='kid-test'),
    path('<str:email>/<str:subject>/TopicInfo', KidExamTopicView.as_view(), name='kid-exam-topic-id'),
    path('<str:email>/<str:subject>/<str:topic>/Info', KidExamSubjectDetail.as_view(), name='kid-exam-subject-id'),

    path('Quiz/<str:email>/<str:name>/', KidTestDetail.as_view(), name='kid-tests-detail'),
    path('<str:email>/<str:uuid>/', KidQuizDetail.as_view(), name='my-kid-test-detail'),
    path('View/<str:email>/progress/', LearnerProgress.as_view(), name='learner-learning-progress'),
    path('<str:name>/<str:email>/syllabus-coverage/', LearnerSyllabus.as_view(), name='learners-syllabus'),

]