from django.db import DatabaseError, IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect

from Teacher.models import ClassTestStudentTest, classTestStudentAnswers
from .models import *
from django.views.generic import TemplateView, DetailView
from itertools import groupby
from SubjectList.models import TopicalExamResults


class Exams(TemplateView):
    template_name = 'Exams/exams.html'

    def get_context_data(self, **kwargs):
        context = super(Exams, self).get_context_data(**kwargs)

        try:
            subject_tests = StudentTest.objects.filter(user=self.request.user).values('topic__subject__name',
                                                                                      'topic__subject__grade',
                                                                                      'topic__name').distinct()
            grouped_subjects = []
            for subject, tests in groupby(subject_tests,
                                          key=lambda x: (x['topic__subject__name'], x['topic__subject__grade'])):
                grade = subject[1]
                topics = [test['topic__name'] for test in tests]
                grouped_subjects.append({'subject': subject[0], 'grade': grade, 'topics': topics})

            context['subjects'] = grouped_subjects

            return context

        except DatabaseError as error:
            pass


class ExamSubjectDetail(TemplateView):
    template_name = 'Exams/subject_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ExamSubjectDetail, self).get_context_data(**kwargs)
        subject = self.kwargs['subject']
        topic = self.kwargs['topic']
        try:
            subject = StudentTest.objects.filter(user=self.request.user, subject__name=subject, topic__name=topic)
            context['subject'] = subject

            return context

        except DatabaseError as error:
            pass


class ExamTopicView(TemplateView):
    template_name = 'Exams/exam_topic_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ExamTopicView, self).get_context_data(**kwargs)

        try:
            subject = StudentTest.objects.filter(user=self.request.user, subject__name=self.kwargs['subject'])\
                .values('topic__name').order_by('topic')
            context['subject'] = subject
            context['subject_name'] = self.kwargs['subject']

            return context

        except DatabaseError as error:
            pass



class TestDetail(TemplateView):
    template_name = 'Exams/test_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TestDetail, self).get_context_data(**kwargs)
        user = self.request.user
        test = str(self.kwargs['uuid'])

        try:
            answers = StudentsAnswers.objects.filter(user=user, test=test)
            topical_test = StudentTest.objects.filter(user=user, uuid=test).last()
            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            else:
                context['base_html'] = 'Users/base.html'
            if not answers and test:
                class_test = ClassTestStudentTest.objects.filter(user=user, test=test).last()
                class_test_answers = classTestStudentAnswers.objects.filter(user=user, test=test)
                print(class_test_answers, class_test)
                context['quizzes'] = class_test_answers
                context['marks'] = class_test

                return context

            else:

                context['quizzes'] = answers
                context['marks'] = topical_test




                return context



        except DatabaseError as error:
            pass


class Start(TemplateView):
    template_name = 'Exams/start.html'

    def get_context_data(self, **kwargs):
        context = super(Start, self).get_context_data(**kwargs)

        try:
            context['topic'] = Topic.objects.filter(name=self.kwargs['pk']).first()

            return context

        except DatabaseError as error:
            pass

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            user = self.request.user
            try:

                topic = Topic.objects.filter(name=self.kwargs['pk']).first()
                try:

                    test = StudentTest.objects.create(user=user,subject=topic.subject, uuid=str(self.kwargs['uuid']), topic=topic)
                    return redirect('tests', topic.name)
                except IntegrityError:
                    pass
                except DatabaseError as error:
                    pass

                finally:
                    self.request.session['testId'] = str(test.uuid)



            except DatabaseError as error:
                pass


class Tests(TemplateView):
    template_name = 'Exams/tests.html'

    def get_context_data(self, **kwargs):
        context = super(Tests, self).get_context_data(**kwargs)
        topic = kwargs['pk']
        question_index = self.request.session.get('index', 0)
        try:
            questions = TopicalQuizes.objects.filter(topic__name=topic)
            print(questions, question_index)

            if question_index >= len(questions):
                return {}

            else:
                current_question = questions[question_index]
                self.request.session['quiz'] = str(current_question)
                try:
                    choices = TopicalQuizAnswers.objects.filter(quiz=current_question)
                    context['choices'] = choices
                    context['quiz'] = current_question
                    context['index'] = question_index + 1
                    numbers = [i + 1 for i in range(len(questions))]
                    context['list'] = numbers

                    return context

                except DatabaseError as error:
                    pass

        except DatabaseError as error:
            pass

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            user = request.user
            topic = kwargs['pk']

            selection = request.POST.get('choice')  # Get the selected choice ID from the POST data

            question_index = request.session.get('index', 0)
            questions = TopicalQuizes.objects.filter(topic__name=topic)
            print(question_index, len(questions))
            quiz = TopicalQuizes.objects.filter(id=request.session['quiz']).first()
            test = StudentTest.objects.filter(uuid=request.session['testId']).first()
            selection = TopicalQuizAnswers.objects.get(uuid=selection)

            try:
                answer = StudentsAnswers.objects.create(user=user, quiz=quiz, selection=selection, test=test)
                if question_index >= len(questions) - 1:
                    # The exam is completed, redirect to a summary page
                    if 'index' in request.session:
                        print('\n\n\n\n\n\n\n, deleting session key')
                        del request.session['index']

                    return redirect('finish', topic)
                else:
                    current_question = questions[question_index]

                    request.session['index'] = question_index + 1
                    return redirect(request.path)
            except IntegrityError as error:
                pass


class Finish(TemplateView):
    template_name = 'Exams/finish.html'

    def get_context_data(self, **kwargs):
        topic = self.kwargs['name']
        context = super(Finish, self).get_context_data(**kwargs)
        user = self.request.user

        try:
            test = StudentTest.objects.filter(user=user, topic__name=topic).order_by('date').last()
            print(test.uuid, '\n\n\n\n\n')
            if test:
                answers = StudentsAnswers.objects.filter(user=user, test=test).values('selection__uuid')
                correct_answers = TopicalQuizAnswers.objects.filter(uuid__in=answers, is_correct='True')
                test.marks = correct_answers.count()
                test.save()
                mark = StudentsAnswers.objects.filter(selection__in=correct_answers)
                for item in mark:
                    item.is_correct = True
                    item.save()
                about = f'The results for {test.topic} on are out.'
                message = f'Congratulations on completing your test. The results' \
                          ' are out, click the button below to view the results. '

                topic = Topic.objects.filter(name=topic).first()
                subject = topic.subject
                try:
                    notifications = TopicalExamResults.objects.create(user=user, test=test.uuid, about=about, message=message, topic=topic, subject=subject)

                except IntegrityError as error:
                    pass
                context['score'] = correct_answers.count()
                context['test'] = test
            else:
                pass

            return context

        except DatabaseError as error:
            pass


