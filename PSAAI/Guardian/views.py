from itertools import groupby
from datetime import datetime

from django.db import DatabaseError
from django.db.models import Count
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from Exams.models import StudentTest, StudentsAnswers
from SubjectList.models import Progress, Topic
from Users.models import MyUser, PersonalProfile


class GuardianHome(TemplateView):
    template_name = 'Guardian/guardian_home.html'

    def get_context_data(self, **kwargs):
        context = super(GuardianHome, self).get_context_data(**kwargs)
        user = self.request.user
        my_uuid = MyUser.objects.get(email=user).uuid
        my_kids = PersonalProfile.objects.filter(ref_id=my_uuid)
        context['kids'] = my_kids
        print(my_kids)

        return context


class MyKidsView(TemplateView):
    template_name = 'Guardian/my_kids_view.html'

    def get_context_data(self, **kwargs):
        context = super(MyKidsView, self).get_context_data(**kwargs)
        user = self.request.user
        my_uuid = MyUser.objects.get(email=user).uuid
        my_kids = PersonalProfile.objects.filter(ref_id=my_uuid)
        context['kids'] = my_kids
        context['current_time'] = datetime.now()

        return context


class TaskSelection(TemplateView):
    template_name = 'Guardian/task_select.html'

    def get_context_data(self, **kwargs):
        context = super(TaskSelection, self).get_context_data(**kwargs)

        context['email'] = self.kwargs['email']
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'

        return context


class KidTests(TemplateView):
    template_name = 'Guardian/kid_tests.html'

    def get_context_data(self, **kwargs):
        context = super(KidTests, self).get_context_data(**kwargs)
        kid = self.kwargs['email']
        subject_tests = StudentTest.objects.filter(user__email=kid).values('topic__subject__name',
                                                                            'topic__subject__grade',
                                                                            'topic__name').distinct()
        grouped_subjects = []
        for subject, tests in groupby(subject_tests,
                                      key=lambda x: (x['topic__subject__name'], x['topic__subject__grade'])):
            grade = subject[1]
            topics = [test['topic__name'] for test in tests]
            grouped_subjects.append({'subject': subject[0], 'grade': grade, 'topics': topics})

        context['subjects'] = grouped_subjects
        context['child'] = kid
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        return context


class KidExamTopicView(TemplateView):
    template_name = 'Guardian/kid_exam_topic_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidExamTopicView, self).get_context_data(**kwargs)
        user = self.kwargs['email']

        try:
            subject = StudentTest.objects.filter(user__email=user, subject__name=self.kwargs['subject'])\
                .values('topic__name').order_by('topic')
            context['subject'] = subject
            context['subject_name'] = self.kwargs['subject']
            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            context['email'] = MyUser.objects.filter(email=user).first()

            return context

        except DatabaseError as error:
            pass


class KidExamSubjectDetail(TemplateView):
    template_name = 'Guardian/kid_subject_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidExamSubjectDetail, self).get_context_data(**kwargs)
        subject = self.kwargs['subject']
        topic = self.kwargs['topic']
        user = self.kwargs['email']
        user = MyUser.objects.filter(email=user).first()
        try:
            subject = StudentTest.objects.filter(user=user, subject__name=subject, topic__name=topic)
            context['subject'] = subject
            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            context['email'] = user


            return context

        except DatabaseError as error:
            pass


class KidTestDetail(TemplateView):
    template_name = 'Guardian/kid_test_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidTestDetail, self).get_context_data(**kwargs)
        subject = self.kwargs['name']
        email = self.kwargs['email']
        subject = StudentTest.objects.filter(user__email=email, subject__name=subject)
        context['tests'] = subject
        context['email'] = email
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'

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
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'

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
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
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
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'

        return context
