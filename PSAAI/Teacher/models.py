from django.db import models

# Create your models here.
from SubjectList.models import Subject
from Users.models import MyUser


class TeacherProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    subject = models.ManyToManyField(Subject)

    def __str__(self):
        return str(self.user)


class StudentList(models.Model):
    user = models.OneToOneField(MyUser,related_name='teacher_user', on_delete=models.CASCADE)
    students = models.ManyToManyField(MyUser)

    def __str__(self):
        return str(self.user)


