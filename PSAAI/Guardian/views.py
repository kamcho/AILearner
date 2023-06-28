from itertools import groupby

from django.db.models import Count
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, TemplateView

from Exams.models import StudentTest, StudentsAnswers
from SubjectList.models import Progress, Topic
from Users.models import MyUser, PersonalProfile


class MyKidsView(TemplateView):
    template_name = 'Guardian/my_kids_view.html'

    def get_context_data(self, **kwargs):
        context = super(MyKidsView, self).get_context_data(**kwargs)
        user = self.request.user
        my_uuid = MyUser.objects.get(email=user).uuid
        my_kids = PersonalProfile.objects.filter(ref_id=my_uuid)
        context['kids'] = my_kids

        return context


class TaskSelection(TemplateView):
    template_name = 'Guardian/task_select.html'

    def get_context_data(self, **kwargs):
        context = super(TaskSelection, self).get_context_data(**kwargs)

        context['email'] = self.kwargs['email']

        return context


class KidTests(TemplateView):
    template_name = 'Guardian/kid_tests.html'

    def get_context_data(self, **kwargs):
        context = super(KidTests, self).get_context_data(**kwargs)
        user = self.kwargs['user']
        subject_tests = StudentTest.objects.filter(user__email=user).values('topic__subject__name',
                                                                            'topic__subject__grade',
                                                                            'topic__name').distinct()

        grouped_subjects = []
        for subject, tests in groupby(subject_tests,
                                      key=lambda x: (x['topic__subject__name'], x['topic__subject__grade'])):
            grade = subject[1]
            topics = [test['topic__name'] for test in tests]
            grouped_subjects.append({'subject': subject[0], 'grade': grade, 'topics': topics})

        context['subjects'] = grouped_subjects
        context['child'] = user
        return context


class KidTestDetail(TemplateView):
    template_name = 'Guardian/kid_test_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidTestDetail, self).get_context_data(**kwargs)
        subject = self.kwargs['name']
        email = self.kwargs['user']
        subject = StudentTest.objects.filter(user__email=email, subject__name=subject)
        context['tests'] = subject
        context['email'] = email

        return context


class KidQuizDetail(TemplateView):
    template_name = 'Guardian/kid_quiz_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidQuizDetail, self).get_context_data(**kwargs)
        mail = self.kwargs['email']
        user = MyUser.objects.get(email=mail)
        test = str(self.kwargs['uuid'])
        answers = StudentsAnswers.objects.filter(user=user, test=test)
        test = StudentTest.objects.get(user=user, uuid=test)

        context['quizzes'] = answers
        context['marks'] = test

        return context


class LearnerProgress(TemplateView):
    template_name = 'Guardian/learner_progress.html'

    def get_context_data(self, **kwargs):
        context = super(LearnerProgress, self).get_context_data(**kwargs)
        email = self.kwargs['email']
        user = MyUser.objects.get(email=email)
        subject = Progress.objects.filter(user=user, subject__isnull=False).values('subject__name',
                                                                                   'subject__topics').annotate(
            topic_count=Count('topic', distinct=True))

        context['subject'] = subject
        return context


class LearnerSyllabus(TemplateView):
    template_name = 'Guardian/learners_syllabus.html'

    def get_context_data(self, **kwargs):
        context = super(LearnerSyllabus, self).get_context_data(**kwargs)
        print(self.kwargs['name'])
        subject = self.kwargs['name']
        coverage = Topic.objects.filter(subject__name=subject).order_by('order')
        context['email'] = self.kwargs['email']
        context['syllabus'] = coverage
        print(coverage)

        return context