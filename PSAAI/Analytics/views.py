from django.db.models import Count
from django.shortcuts import render
from django.views.generic import TemplateView

from Exams.models import *
from Teacher.models import *


# Create your views here.


class OverallAnalytics(TemplateView):
    template_name = 'Analytics/overall_analytics.html'

    def get_context_data(self, **kwargs):
        context = super(OverallAnalytics, self).get_context_data(**kwargs)
        user = self.request.user
        tests = StudentTest.objects.filter(user=user).values('subject__name', 'topic__name').annotate(
            Count('topic')).order_by('subject__name')
        context['tests'] = tests

        return context


class SubjectAnalytics(TemplateView):
    template_name = 'Analytics/subject_analytics.html'

    def get_context_data(self, **kwargs):
        context = super(SubjectAnalytics, self).get_context_data(**kwargs)
        user = self.request.user
        subject = self.kwargs['subject']
        subject = Subject.objects.filter(name=subject).first()

        student_tests = StudentTest.objects.filter(user=user, subject__name=subject)
        class_test = ClassTestStudentTest.objects.filter(user=user, test__subject__name=subject)
        context['total_tests'] = int(student_tests.count()) + int(class_test.count())

        weakness = StudentsAnswers.objects.filter(user=user, quiz__subject__name=subject, is_correct=False). \
            values('quiz__topic__name').order_by('quiz__topic__name')
        class_weakness = classTestStudentAnswers.objects.filter(user=user, quiz__subject__name=subject, is_correct=False). \
            values('quiz__topic__name').annotate(
            Count('quiz__topic__name')).order_by('quiz__topic__name')
        strength = StudentsAnswers.objects.filter(user=user, quiz__subject__name=subject, is_correct=True). \
            values('quiz__topic__name').order_by('quiz__topic__name')
        class_strength = classTestStudentAnswers.objects.filter(user=user, quiz__subject__name=subject, is_correct=True). \
            values('quiz__topic__name').annotate(
            Count('quiz__topic__name')).order_by('quiz__topic__name')

        context['strength'] = class_strength
        context['weakness'] = class_weakness

        return context
