import datetime

from django.db import models
import uuid

from Users.models import MyUser


class Course(models.Model):
    name = models.CharField(max_length=100)
    discipline = models.CharField(max_length=20, default="science")

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=1)
    grade = models.CharField(max_length=2, default="1")
    topics = models.PositiveIntegerField(default='6')
    course = models.ForeignKey(Course, default=1, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class MySubjects(models.Model):
    name = models.ManyToManyField(Course, blank=True, related_name='my_subjects')
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def selected(self):
        if self.name.exists():
            return 'True'
        else:
            return 'False'


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.IntegerField(default=1)
    subject = models.ForeignKey(Subject, related_name='subject_id', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    topics_count = models.CharField(max_length=5, default='4')

    def __str__(self):
        return self.name


class Subtopic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, default='9', on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='topic')
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='studyFiles', default='file.pdf')
    order = models.CharField(max_length=5, default='1')

    def __str__(self):
        return self.name


class Progress(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic, related_name='progress')

    def __str__(self):
        return str(self.user)


class Notifications(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(MyUser, default='1', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=100, default='payment')
    message = models.TextField(max_length=500)
    about = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class TopicExamNotifications(Notifications):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class TopicalExamResults(Notifications):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.CASCADE)
    test = models.UUIDField()

    def __str__(self):
        return str(self.user)


class OnlineClass(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    date = models.DateTimeField()
    duration = models.IntegerField()
    link = models.CharField(max_length=100, default='google.classroom.org/tyu565ffy')

    def __str__(self):
        return self.name

    # noinspection PyTypeChecker
    def end_time(self):
        end_time = self.date + datetime.timedelta(minutes=self.duration)

        return end_time


class ClassBookingNotifications(Notifications):
    class_id = models.ForeignKey(OnlineClass, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class SubscriptionNotifications(Notifications):
    subs = models.CharField(max_length=200)

    def __str__(self):
        return str(self.user)


class PaymentNotifications(Notifications):
    amount = models.PositiveIntegerField(default='1')
    subscription_type = models.CharField(max_length=200)
    beneficiaries = models.CharField(max_length=100, default='njokevin9@gmail.com')

    def __str__(self):
        return str(self.user)


class ClassBooking(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    class_name = models.ForeignKey(OnlineClass, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class VideoChannel(models.Model):
    class_id = models.ForeignKey(OnlineClass, on_delete=models.CASCADE)
    app_id = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=300, unique=True)
    date = models.DateField(auto_created=True)

    def __str__(self):
        return self.channel_name


class AgoraLearners(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    channel = models.ForeignKey(VideoChannel, unique=True, to_field='channel_name', on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return self.user


class UserInquiries(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    quiz_class = models.CharField(max_length=30)
    date = models.DateField(auto_now=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4)

    class Meta:
        abstract = True


class AcademicInquiries(UserInquiries):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    message = models.TextField(max_length=500)


class AccountInquiries(UserInquiries):
    message = models.TextField(max_length=500)
