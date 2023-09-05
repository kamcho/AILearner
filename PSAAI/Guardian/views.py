from abc import ABC
from itertools import groupby
from datetime import datetime

from django.contrib import messages
from django.db import DatabaseError
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from Exams.models import StudentTest, StudentsAnswers, ClassTestStudentTest, StudentKNECExams, StudentsKnecAnswers
from SubjectList.models import Progress, Topic

from Users.models import MyUser, PersonalProfile


class GuardianHome(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        Guardians Home Page
    """
    template_name = 'Guardian/guardian_home.html'

    def get_context_data(self, **kwargs):
        context = super(GuardianHome, self).get_context_data(**kwargs)
        user = self.request.user.uuid  # get user
        try:
            # Get learners linked to logged in guardian
            my_kids = PersonalProfile.objects.filter(ref_id=user)  # get linked kids account
            context['kids'] = my_kids
        except (Exception,):
            # Handle any exceptions
            messages.error(self.request, 'An exception occurred were fixing it')

        return context

    def test_func(self):
        return self.request.user.role == 'Guardian'


class MyKidsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        Guardian view of linked accounts
    """
    template_name = 'Guardian/my_kids_view.html'

    def get_context_data(self, **kwargs):
        context = super(MyKidsView, self).get_context_data(**kwargs)
        user = self.request.user.uuid
        try:
            # Get learners linked to logged in guardian
            my_kids = PersonalProfile.objects.filter(ref_id=user)
            context['kids'] = my_kids
            context['current_time'] = datetime.now()  # Get current time
        except Exception:
            messages.error(self.request, 'DataBase Error were fixing it')

        return context

    def test_func(self):
        return self.request.user.role in ['Guardian', 'Teacher']


class TaskSelection(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        Choose to view a learners tests or learning progress
    """
    template_name = 'Guardian/task_select.html'

    def get_context_data(self, **kwargs):
        context = super(TaskSelection, self).get_context_data(**kwargs)

        context['email'] = self.kwargs['email']  # Get a students email from url

        # choose which base template to use based on roles
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'

        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role in ['Guardian', 'Teacher']:

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True

        return False


class KidTests(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        View linked students test
    """
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

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role in ['Guardian', 'Teacher']:

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True

        return False


class KidExamTopicView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Guardian/kid_exam_topic_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidExamTopicView, self).get_context_data(**kwargs)
        user = self.kwargs['email']

        try:
            subject = StudentTest.objects.filter(user__email=user, subject__name=self.kwargs['subject']) \
                .values('topic__name').order_by('topic').distinct()
            context['subject'] = subject
            knec_test = StudentKNECExams.objects.filter(user__email=user)
            context['tests'] = knec_test
            class_test = ClassTestStudentTest.objects.filter(user__email=user).exclude(
                uuid='c2f49d23-41eb-457a-a147-8e132751774c')
            context['class_tests'] = class_test
            context['subject_name'] = self.kwargs['subject']
            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            context['email'] = MyUser.objects.filter(email=user).first()

            return context

        except DatabaseError as error:
            pass

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role in ['Guardian', 'Teacher']:

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True

        return False


class KidExamSubjectDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
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

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role in ['Guardian', 'Teacher']:

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True

        return False


class KidTestDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
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

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role in ['Guardian', 'Teacher']:

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True

        return False


class KidTestRevision(LoginRequiredMixin, UserPassesTestMixin, TemplateView, ABC):
    template_name = 'Guardian/kid_quiz_detail.html'

    def get_context_data(self, **kwargs):
        context = super(KidTestRevision, self).get_context_data(**kwargs)
        user = self.kwargs['email']
        test = str(self.kwargs['uuid'])
        instance = self.kwargs['instance']
        user = MyUser.objects.filter(email=user).first()

        try:
            if instance == 'Topical':
                answers = StudentsAnswers.objects.filter(user=user, test_object_id=test)
                test = StudentTest.objects.filter(user=user, uuid=test).last()
            elif instance == 'KNECExams':
                test = StudentKNECExams.objects.filter(user=user, test=test).last()
                answers = StudentsKnecAnswers.objects.filter(user=user, test=test)
            elif instance == 'ClassTests':
                answers = StudentsAnswers.objects.filter(user=user, test_object_id=test)
                test = ClassTestStudentTest.objects.filter(user=user, test=test).last()
            else:
                pass

            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            else:
                context['base_html'] = 'Users/base.html'

            context['quizzes'] = answers
            context['marks'] = test

            return context

        except DatabaseError as error:
            pass

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role in ['Guardian', 'Teacher']:

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True

        return False


class LearnerProgress(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        View linked students learning progress
    """
    template_name = 'Guardian/learner_progress.html'


    def get_context_data(self, **kwargs):
        context = super(LearnerProgress, self).get_context_data(**kwargs)
        email = self.kwargs['email']  # Get students email from url
        try:
            # Get students progress
            subject = Progress.objects.filter(user__email=email, subject__isnull=False).values('subject__name',
                                                                                               'subject__topics').annotate(
                topic_count=Count('topic', distinct=True))

            # Choose base template based on role
            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            context['subject'] = subject

        except (Exception,):
            # Handle any exceptions
            messages.error(self.request, 'An error occurred, were fixing it')
        return context

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role in ['Guardian', 'Teacher']:

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True

        return False


class LearnerSyllabus(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        View students syllabus
    """
    template_name = 'Guardian/learners_syllabus.html'

    def test_func(self):
        email = self.kwargs.get('email')
        user = self.request.user

        # Check if the user has a 'Guardian' or 'Teacher' role
        if user.role in ['Guardian', 'Teacher']:

            # Attempt to get the student's profile using the provided email
            try:
                student = PersonalProfile.objects.get(ref_id=user.uuid, user__email=email)
            except Exception:
                messages.error(self.request, 'You can"t view this student')
                return False

            # Ensure the student is associated with the logged-in user
            if student.ref_id == user.uuid:
                return True

        return False

    def get_context_data(self, **kwargs):
        context = super(LearnerSyllabus, self).get_context_data(**kwargs)
      
        subject = self.kwargs['name']  # Get subject from url
        try:
            # Get all topics by subject
            coverage = Topic.objects.filter(subject__name=subject).order_by('order')

            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'

        except Exception:
            # Handle any exceptions
            messages.error(self.request, 'An error occurred we are fixing it')
        context['email'] = self.kwargs['email']
        context['syllabus'] = coverage

        return context
