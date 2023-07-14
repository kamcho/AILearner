import uuid

from django.db import models
from SubjectList.models import Topic, Subject, Subtopic
# Create your models here.
from SubjectList.models import Course
import datetime

from Users.models import MyUser


class TopicalQuizes(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    quiz = models.TextField(max_length=500)

    def __str__(self):
        return str(self.id)


class TopicalQuizAnswers(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    quiz = models.ForeignKey(TopicalQuizes, on_delete=models.CASCADE)
    choice = models.CharField(max_length=600)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class StudentTest(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=100, default=uuid.uuid4, unique=True)
    date = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.CharField(max_length=100,default='0')

    def __str__(self):
        return str(self.user)


class StudentsAnswers(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    quiz = models.ForeignKey(TopicalQuizes, on_delete=models.CASCADE)
    selection = models.ForeignKey(TopicalQuizAnswers, on_delete=models.CASCADE)
    test = models.ForeignKey(StudentTest,to_field='uuid', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

