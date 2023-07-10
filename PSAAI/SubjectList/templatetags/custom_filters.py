from django import template
from django.shortcuts import redirect

from Exams.models import StudentTest
from SubjectList.models import *
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
        test = StudentTest.objects.get(user=user, uuid=test_uuid)
        return True

    except StudentTest.DoesNotExist:
        return False
    except StudentTest.MultipleObjectsReturned:
        return False



