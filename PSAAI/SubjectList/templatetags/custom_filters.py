from django import template

from SubjectList.models import Progress, Subject, Course, Topic

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

    subjects = Subject.objects.get(name=subject)
    progress = Progress.objects.filter(user=user, subject=subjects).last()
    introduction = Topic.objects.get(subject=subjects, order=1)

    if progress:
        number = progress.topic.last().order
        next_topic = Topic.objects.get(subject=progress.subject, order=int(number) + 1)
        return next_topic
    else:
        # Return the first topic in the subject
        return introduction
    return subject
