import uuid

from django.db import models
from SubjectList.models import Topic
# Create your models here.
from SubjectList.models import Course
import datetime



class TopicalQuizes(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    quiz = models.TextField(max_length=500)

    def __str__(self):
        return str(self.id)


class TopicalQuizAnswers(models.Model):
    quiz = models.ForeignKey(TopicalQuizes, on_delete=models.CASCADE)
    choice = models.CharField(max_length=600)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)