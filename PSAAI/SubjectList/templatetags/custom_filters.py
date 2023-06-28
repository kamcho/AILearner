from django import template
from django.shortcuts import redirect

from SubjectList.models import Progress, Subject, Course, Topic, Subtopic
from Users.models import MyUser

register = template.Library()


@register.filter
def divide(value, arg):
    value = int(value)
    try:
        return round((value / arg) * 100)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def get_user_progress_topic(user, subject):
    subject = Subject.objects.get(name=subject)
    progress = Progress.objects.filter(user=user, subject=subject).last()
    if progress:
        current_subtopic = Subtopic.objects.get(name=progress.subtopic)
        return current_subtopic
    else:
        introduction = Topic.objects.get(subject=subject, order=1)
        introduction = Subtopic.objects.get(topic=introduction, order=1)
        return introduction


@register.filter
def topic_in_progress(user, topic):
    try:
        progress = Progress.objects.filter(user=user, topic=topic)
        if progress.exists():
            return True
        else:
            return False

    except:
        return redirect('home')

@register.filter
def guardian_topic_view(email, topic):
    try:
        user = MyUser.objects.get(email=email)

        progress = Progress.objects.filter(user=user, topic=topic)
        if progress.exists():
            return True
        else:
            return False

    except:
        return redirect('home')

@register.filter
def subtopic_in_progress(user,subtopic):
    try:
        progress = Progress.objects.filter(user=user, subtopic=subtopic)
        if progress.exists():
            return True
        else:
            return False

    except:
        return redirect('home')

@register.filter
def guardian_subtopic_view(email,subtopic):
    try:
        user = MyUser.objects.get(email=email)
        progress = Progress.objects.filter(user=user, subtopic=subtopic)
        if progress.exists():
            return True
        else:
            return False

    except:
        return redirect('home')

