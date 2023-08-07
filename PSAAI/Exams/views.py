from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError, IntegrityError
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect

from Teacher.models import ClassTestStudentTest, classTestStudentAnswers
from .models import *
from django.views.generic import TemplateView, DetailView
from itertools import groupby
from SubjectList.models import TopicalExamResults, TopicExamNotifications


class Exams(LoginRequiredMixin, TemplateView):
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


class ExamSubjectDetail(LoginRequiredMixin, TemplateView):
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


class ExamTopicView(LoginRequiredMixin, TemplateView):
    template_name = 'Exams/exam_topic_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ExamTopicView, self).get_context_data(**kwargs)

        try:
            subject = StudentTest.objects.filter(user=self.request.user, subject__name=self.kwargs['subject']) \
                .values('topic__name').order_by('topic')
            context['subject'] = subject
            context['subject_name'] = self.kwargs['subject']

            return context

        except DatabaseError as error:
            pass


class TestDetail(LoginRequiredMixin, TemplateView):
    template_name = 'Exams/test_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TestDetail, self).get_context_data(**kwargs)
        user = self.request.user
        test = str(self.kwargs['uuid'])

        try:
            answers = StudentsAnswers.objects.filter(user=user, test=test)
            topical_test = StudentTest.objects.filter(user=user, uuid=test).last()
            context['quizzes'] = answers
            context['marks'] = topical_test
            if not answers and test:

                class_test = ClassTestStudentTest.objects.filter(user=user, test=test).last()
                print(class_test)
                class_test_answers = classTestStudentAnswers.objects.filter(user=user, test=test)
                print(class_test_answers, class_test)
                context['quizzes'] = class_test_answers
                context['marks'] = class_test

            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            else:
                context['base_html'] = 'Users/base.html'

            return context


        except DatabaseError as error:
            pass


class StartRepeat(TemplateView):
    template_name = 'Exams/repeat_start.html'

    def get_context_data(self, **kwargs):
        context = super(StartRepeat, self).get_context_data(**kwargs)
        user = self.request.user
        test_id = self.kwargs['uuid']
        test = StudentTest.objects.filter(user=user, uuid=test_id).last()
        quiz = test.quiz.all()
        topics = TopicalQuizes.objects.filter(id__in=quiz).values('topic__name').annotate(
            topic_count=Count('topic__name')).order_by('topic__name')

        context['quizes'] = topics

        context['test'] = test
        return context

    def post(self, request, **kwargs):
        if self.request.method == 'POST':
            test_uuid = self.kwargs['uuid']

            return redirect('tests', test_uuid)


class Start(LoginRequiredMixin, TemplateView):
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
            topic_name = self.kwargs['pk']
            test_uuid = self.kwargs['uuid']
            try:
                topic = Topic.objects.filter(name=topic_name).first()
                try:
                    test = StudentTest.objects.create(user=user, subject=topic.subject, uuid=str(test_uuid),
                                                      topic=topic)
                    print
                    quizzes = TopicalQuizes.objects.filter(topic=topic)
                    test.quiz.add(*quizzes)
                    return redirect('tests', test.uuid)
                except IntegrityError:
                    pass
                except DatabaseError as error:
                    pass



            except DatabaseError as error:
                pass


class Tests(LoginRequiredMixin, TemplateView):
    template_name = 'Exams/tests.html'

    def get_context_data(self, **kwargs):
        context = super(Tests, self).get_context_data(**kwargs)
        test_id = kwargs['uuid']
        user = self.request.user
        question_index = self.request.session.get('index', 0)
        try:
            questions = StudentTest.objects.filter(user=user, uuid=test_id).first()
            print(questions, question_index)

            if question_index >= len(questions.quiz.all()):
                return {}

            else:
                current_question = questions.quiz.all()[question_index]
                self.request.session['quiz'] = str(current_question)
                try:
                    choices = TopicalQuizAnswers.objects.filter(quiz=current_question).order_by('?')
                    context['choices'] = choices
                    context['quiz'] = current_question
                    context['index'] = question_index + 1
                    numbers = [i + 1 for i in range(len(questions.quiz.all()))]
                    context['list'] = numbers

                    return context

                except DatabaseError as error:
                    pass

        except DatabaseError as error:
            pass

    def post(self, request, *args, **kwargs):

        if request.method == 'POST':
            user = request.user
            # topic = kwargs['pk']
            test_id = kwargs['uuid']
            selection = request.POST.get('choice')  # Get the selected choice ID from the POST data

            question_index = request.session.get('index', 0)
            test = StudentTest.objects.filter(user=user, uuid=test_id).first()
            ids = test.quiz.all()
            questions = TopicalQuizes.objects.filter(id__in=ids)
            # print(question_index, len(questions))
            quiz = TopicalQuizes.objects.filter(id=request.session['quiz']).first()
            selection = TopicalQuizAnswers.objects.filter(uuid=selection).first()
            print('\n\n\n\n\n\n\n',selection)
            correct = TopicalQuizAnswers.objects.filter(uuid=selection.uuid, is_correct=True).first()
            if correct:
                test.marks = int(test.marks) + 1
                test.save()
                is_correct = True

            else:
                is_correct = False

            try:
                answer = StudentsAnswers.objects.create(user=user, quiz=quiz, selection=selection, is_correct=is_correct, test=test)
                if question_index >= len(questions) - 1:
                    # The exam is completed, redirect to a summary page
                    if 'index' in request.session:
                        print('\n\n\n\n\n\n\n, deleting session key')
                        del request.session['index']



                        return redirect('finish', test_id)

                else:
                    current_question = questions[question_index]

                    request.session['index'] = question_index + 1
                    return redirect(request.path)
            except IntegrityError as error:
                pass


class Finish(LoginRequiredMixin, TemplateView):
    template_name = 'Exams/finish.html'

    def get_context_data(self, **kwargs):
        context = super(Finish, self).get_context_data(**kwargs)
        test_id = self.kwargs['uuid']
        # topic = self.kwargs['pk']
        user = self.request.user
        try:
            test = StudentTest.objects.filter(user=user, uuid=test_id).order_by('date').last()
            print(test.uuid, '\n\n\n\n\n')
            about = f'The results for {test.topic} on are out.'
            message = f'Congratulations on completing your test. The results' \
                      ' are out, click the button below to view the results. '

            try:
                topic = Topic.objects.filter(name=test.topic).first()
                subject = topic.subject
                notifications = TopicalExamResults.objects.create(user=user, test=test.uuid, about=about,
                                                                  message=message, subject=subject, topic=topic)
            except:
                notifications = TopicalExamResults.objects.create(user=user, test=test.uuid, about=about,
                                                                  message=message,  subject=test.subject)
        except IntegrityError as error:
            pass


        except DatabaseError as error:
            pass

        finally:
            context['score'] = test.marks
            context['test'] = test

            return context




class SetTest(TemplateView):
    template_name = 'Exams/set_test.html'

    def get_context_data(self, **kwargs):
        context = super(SetTest, self).get_context_data(**kwargs)
        subject = self.kwargs['subject']
        topics = Topic.objects.filter(subject__name=subject)

        context['topics'] = topics

        return context

    def post(self, request, **kwargs):
        if self.request.method == "POST":
            user = self.request.user
            subject = self.kwargs['subject']
            subject = Subject.objects.filter(name=subject).first()
            topics = self.request.POST.getlist('topics')
            test_size = self.request.POST.get('size')
            test_size = int(test_size)
            test_id = uuid.uuid4()
            about = 'You have a new test. View more info below.'
            message = 'The test you requested is now available, Good luck.'
            notification = TopicExamNotifications.objects.create(user=user, about=about,
                                                                 notification_type='retake', uuid=test_id,
                                                                 subject=subject, message=message,
                                                                 )
            test = StudentTest.objects.create(user=user, subject=subject, uuid=test_id)
            failed_quiz = StudentsAnswers.objects.filter(is_correct=False, quiz__topic__in=topics).order_by('?')[:3]
            quizes = TopicalQuizes.objects.filter(topic__in=topics)
            done_quiz = StudentsAnswers.objects.filter(quiz__topic__in=topics)

            new_quiz = quizes.exclude(id__in=done_quiz).order_by('?')[:test_size - 3]
            failed_count = int(failed_quiz.count())
            new_count = int(new_quiz.count())

            if failed_count >= 3 and new_count >= 12:
                test.quiz.add(*failed_quiz)

                test.quiz.add(*new_quiz)



            elif failed_count <= 3 and new_count >= 12:
                # new_quiz = quizes.exclude(uuid__in=done_quiz).order_by('?')[:(test_size-failed_count)]
                test.quiz.add(*failed_quiz)

                test.quiz.add(*new_quiz)

                quizzes = quizes.order_by('?')[:test_size]
                test.quiz.add(*quizzes)


            else:
                questions = TopicalQuizes.objects.filter(topic__in=topics).order_by('?')[:test_size]
                test.quiz.add(*questions)

            return redirect('student-home')
