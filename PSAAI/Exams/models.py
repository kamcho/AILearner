from django.db import models
from SubjectList.models import Topic
# Create your models here.
from SubjectList.models import Course
import datetime



class KCSEExam(models.Model):
    year = models.DateField()
    subject = models.ForeignKey(Course,on_delete=models.CASCADE)
    unit = models.CharField(max_length=20)

    def __str__(self):

        return str(self.subject) + ' ' + str(self.year.strftime('%Y'))

class KCSEQuiz(models.Model):
    unit = models.ForeignKey(KCSEExam,on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    section = models.CharField(max_length=10)
    quiz = models.TextField(max_length=500)
    number = models.IntegerField()

    def __str__(self):
        return str(self.unit) + ' ' + str(self.number)

class KCSEAnswers(models.Model):
    quiz = models.ForeignKey(KCSEQuiz,on_delete=models.CASCADE)
    answer = models.TextField(max_length=1500)

    def __str__(self):

        return str(self.quiz)

class TopicalQuiz(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    quiz = models.TextField(max_length=500)

    def __str__(self):
        return str(self.id)

class TopicalQuizAnswer(models.Model):
    quiz = models.ForeignKey(TopicalQuiz, on_delete=models.CASCADE)
    answer = models.TextField(max_length=500)

    def __str__(self):
        return str(self.id)