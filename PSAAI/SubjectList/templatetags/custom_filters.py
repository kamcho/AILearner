from django import template
from django.db.models import Sum
from django.shortcuts import redirect
import datetime

from Exams.models import StudentTest
from SubjectList.models import *
from Teacher.models import ClassTestStudentTest, ClassTest
from Users.models import MyUser

register = template.Library()


@register.filter
def divide(value, arg):
    try:
        value = int(value)
        return round((value / arg) * 100)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def get_user_progress_topic(user, subject):
    subject = Subject.objects.filter(name=subject).first()
    progress = Progress.objects.filter(user=user, subject=subject).last()
    if progress:
        try:
            current_subtopic = Subtopic.objects.filter(name=progress.subtopic).last()
            return current_subtopic

        except Subtopic.DoesNotExist:
            try:
                introduction = Topic.objects.get(subject=subject, order=1)
                introduction = Subtopic.objects.get(topic=introduction, order=1)
                print(introduction)
                return introduction
            except Topic.DoesNotExist:
                return None
            except Subtopic.DoesNotExist:
                return None
    else:
        try:
            introduction = Topic.objects.get(subject=subject, order=1)
            introduction = Subtopic.objects.get(topic=introduction, order=1)
            print(introduction)
            return introduction
        except Topic.DoesNotExist:
            return None
        except Subtopic.DoesNotExist:
            return None


@register.filter
def topic_in_progress(user, topic):
    try:
        progress = Progress.objects.filter(user=user, topic=topic)
        if progress.exists():
            return True
        else:
            return False

    except Progress.DoesNotExist:
        return False


@register.filter
def guardian_topic_view(email, topic):
    try:
        user = MyUser.objects.get(email=email)
        progress = Progress.objects.filter(user=user, topic=topic)
        if progress.exists():
            return True
        else:
            return False

    except Progress.DoesNotExist:
        pass

    except MyUser.DoesNotExist:
        pass


@register.filter
def subtopic_in_progress(user, subtopic):
    try:
        progress = Progress.objects.filter(user=user, subtopic=subtopic)
        if progress.exists():
            return True
        else:
            return False

    except Progress.DoesNotExist:
        pass


@register.filter
def guardian_subtopic_view(email, subtopic):
    try:
        user = MyUser.objects.get(email=email)
        progress = Progress.objects.filter(user=user, subtopic=subtopic)
        if progress.exists():
            return True
        else:
            return False

    except MyUser.DoesNotExist:
        pass

    except Progress.DoesNotExist:
        pass


@register.filter
def class_is_booked(user, class_id):
    try:
        booking = ClassBooking.objects.filter(user=user, class_name=class_id)
        if booking.exists():
            print(class_id)
            return True
        else:
            print("not found", class_id)
            return False

    except ClassBooking.DoesNotExist:
        return False


@register.filter
def test_is_done(user, test_uuid):
    try:
        class_test = ClassTestStudentTest.objects.filter(user=user, test=test_uuid).first()
        test = StudentTest.objects.filter(user=user, uuid=test_uuid).first()
        if test or class_test:

            return True
        else:
            return False

        return True

    except DatabaseError:
        return False


@register.filter
def class_test_progress(test_uuid):
    class_test = ClassTest.objects.filter(uuid=test_uuid).last()
    class_id = class_test.class_id
    student_count = SchoolClass.objects.filter(class_name=class_id).first()
    test_count = ClassTestStudentTest.objects.filter(test=test_uuid).count()

    return f' {test_count} / {student_count.class_size} '


@register.filter
def class_test_average(test_uuid):
    tests = ClassTestStudentTest.objects.filter(test=test_uuid)
    test = ClassTest.objects.filter(uuid=test_uuid).first()
    total_marks = tests.aggregate(total_marks=Sum('marks'))['total_marks']
    average = (int(total_marks) / int(tests.count()))

    return f'{average} / {test.test_size} '


@register.filter
def class_test_active(date):
    if datetime.date.today() > date:
        return True
    else:
        return False


@register.filter
def split_value(value, delimiter):
    return value.split(delimiter)[0]

@register.filter
def topical_average(user, topic):
    tests = StudentTest.objects.filter(user=user, topic__name=topic)


    total_marks = tests.aggregate(total_marks=Sum('marks'))['total_marks']
    average = (int(total_marks) / int(tests.count()))
    return average

@register.filter
def topical_average_count(user, topic):
    tests = StudentTest.objects.filter(user=user, topic__name=topic)
    return tests.count()
