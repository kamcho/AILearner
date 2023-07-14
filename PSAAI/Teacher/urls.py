from django.urls import path
from .views import *
from . import views



urlpatterns = [
    path('', TeacherView.as_view(), name='teachers-home'),
    path('Class/', ClassView.as_view(), name='class'),

    path('Add-Questions/', CreateQuestion.as_view(), name='create-questions'),
    path('load_topics/', views.load_topic, name='load-topics'),
    path('load_subtopics/', views.load_subtopics, name='load-subtopics'),
    path('Add-Answer/', AddAnswerSelection.as_view(), name='add-answer'),
    path('Save-Question/', SaveQuiz.as_view(), name='save-quiz'),

]
