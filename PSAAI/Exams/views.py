
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from django.views.generic import TemplateView, DetailView
from itertools import groupby
from SubjectList.models import TopicalExamResults


class Exams(TemplateView):
    template_name = 'Exams/exams.html'

    def get_context_data(self, **kwargs):
        context = super(Exams, self).get_context_data(**kwargs)
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


class ExamSubjectDetail(TemplateView):
    template_name = 'Exams/subject_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ExamSubjectDetail, self).get_context_data(**kwargs)
        subject = StudentTest.objects.filter(user=self.request.user, subject__name=self.kwargs['name'])
        context['subject'] = subject

        return context


class TestDetail(TemplateView):
    template_name = 'Exams/test_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TestDetail, self).get_context_data(**kwargs)
        user = self.request.user
        test = str(self.kwargs['uuid'])
        answers = StudentsAnswers.objects.filter(user=user, test=test)
        test = StudentTest.objects.get(user=user, uuid=test)

        context['quizzes'] = answers
        context['marks'] = test

        return context


class Start(TemplateView):
    template_name = 'Exams/start.html'

    def get_context_data(self, **kwargs):
        context = super(Start, self).get_context_data(**kwargs)
        context['topic'] = Topic.objects.get(name=self.kwargs['pk'])

        return context

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            user = self.request.user
            topic = Topic.objects.get(name=self.kwargs['pk'])
            test = StudentTest.objects.create(user=user,subject=topic.subject, uuid=str(self.kwargs['uuid']), topic=topic)
            self.request.session['testId'] = str(test.uuid)

            return redirect('tests', topic.name)

        return HttpResponse('success')


class Tests(TemplateView):
    template_name = 'Exams/tests.html'

    def get_context_data(self, **kwargs):
        context = super(Tests, self).get_context_data(**kwargs)
        topic = kwargs['pk']
        question_index = self.request.session.get('index', 0)
        questions = TopicalQuizes.objects.filter(topic__name=topic)
        print(questions, question_index)

        if question_index >= len(questions):
            return {}

        else:
            current_question = questions[question_index]
            self.request.session['quiz'] = str(current_question)
            choices = TopicalQuizAnswers.objects.filter(quiz=current_question)
            context['choices'] = choices
            context['quiz'] = current_question
            context['index'] = question_index + 1
            numbers = [i + 1 for i in range(len(questions))]
            context['list'] = numbers

            return context

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            user = request.user
            topic = kwargs['pk']

            selection = request.POST.get('choice')  # Get the selected choice ID from the POST data

            question_index = request.session.get('index', 0)
            questions = TopicalQuizes.objects.filter(topic__name=topic)
            print(question_index, len(questions))
            quiz = TopicalQuizes.objects.get(id=request.session['quiz'])
            test = StudentTest.objects.get(uuid=request.session['testId'])
            selection = TopicalQuizAnswers.objects.get(uuid=selection)

            answer = StudentsAnswers.objects.create(user=user, quiz=quiz, selection=selection, test=test)
            if question_index >= len(questions) - 1:
                # The exam is completed, redirect to a summary page
                if 'index' in request.session:
                    del request.session['index']

                return redirect('finish',topic)
            else:
                current_question = questions[question_index]

                request.session['index'] = question_index + 1
                return redirect(request.path)


class Finish(TemplateView):
    template_name = 'Exams/finish.html'



    def get_context_data(self, **kwargs):
        topic = self.kwargs['name']
        context = super(Finish, self).get_context_data(**kwargs)
        user = self.request.user
        test = StudentTest.objects.filter(user=user, topic__name=topic).order_by('date').last()

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

            topic = Topic.objects.get(name=topic)
            subject = topic.subject

            notifications = TopicalExamResults.objects.create(user=user, about=about, message=message, topic=topic, subject=subject)

            context['score'] = correct_answers.count()
            context['test'] = test
        else:
            pass

        return context


