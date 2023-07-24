import uuid as uuid
from django.db import models
import uuid
# Create your models here.
from Exams.models import TopicalQuizes, TopicalQuizAnswers
from SubjectList.models import Subject, Topic, Subtopic, OnlineClass, Notifications
from Users.models import MyUser, SchoolClass


class TeacherProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    subject = models.ManyToManyField(Subject)

    def __str__(self):
        return str(self.user)


class StudentList(models.Model):
    user = models.ForeignKey(MyUser, related_name='teacher_user', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, default='9', on_delete=models.CASCADE)
    class_id = models.ForeignKey(SchoolClass, default='1', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class MyClasses(models.Model):
    user = models.ForeignKey(MyUser, related_name='teachers_class', on_delete=models.CASCADE)
    online_class = models.ForeignKey(OnlineClass, on_delete=models.CASCADE)
    students = models.ManyToManyField(MyUser)

    def __str__(self):
        return str(self.user)


class ClassTest(models.Model):
    uuid = models.CharField(max_length=100, default=uuid.uuid4, primary_key=True, unique=True)
    teacher = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    class_id = models.ForeignKey(SchoolClass, default='1', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test_size = models.PositiveIntegerField()
    duration = models.PositiveIntegerField(default='15')
    quiz = models.ManyToManyField(TopicalQuizes)
    expiry = models.DateField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(str(self.teacher) + ' - ' + str(self.subject))


class ClassTestStudentTest(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    test = models.ForeignKey(ClassTest, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=100, default=uuid.uuid4, unique=True)
    date = models.DateTimeField(auto_now=True)
    marks = models.CharField(max_length=100, default='0')
    finished = models.BooleanField()

    def __str__(self):
        return str(self.user)


class classTestStudentAnswers(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    quiz = models.ForeignKey(TopicalQuizes, on_delete=models.CASCADE)
    selection = models.ForeignKey(TopicalQuizAnswers, on_delete=models.CASCADE)
    test = models.ForeignKey(ClassTest, to_field='uuid', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return str(self.test)


# class StudentTest(models.Model):
#     user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
#     uuid = models.CharField(max_length=100, default=uuid.uuid4, unique=True)
#     date = models.DateTimeField(auto_now=True)
#     topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
#     marks = models.CharField(max_length=100, default='0')
#
#     def __str__(self):
#         return str(self.user)


class ClassTestNotifications(Notifications):
    test = models.ForeignKey(ClassTest, on_delete=models.CASCADE)
    class_id = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.test)
