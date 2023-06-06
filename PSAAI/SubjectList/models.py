from django.db import models

# Create your models here.


from django.db import models
import uuid

from Users.models import MyUser



class Course(models.Model):
    name = models.CharField(max_length=100)
    discipline = models.CharField(max_length=20,default="science")

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    grade= models.CharField(max_length=2,default="1")

    def __str__(self):
        return self.name + ' ' + self.grade
class MySubjects(models.Model):
    name = models.ManyToManyField(Course,blank=True,related_name='my_subjects')
    user = models.OneToOneField(MyUser,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.user)
#
class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subtopic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='studyFiles',default='file.pdf')

    def __str__(self):
        return self.name
