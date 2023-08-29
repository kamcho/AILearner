import datetime
from sqlite3 import OperationalError

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import DatabaseError, IntegrityError
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect

# from Teacher.models import ClassTestStudentTest
from Supervisor.models import KnecQuizAnswers
from Users.models import PersonalProfile, AcademicProfile
from .models import *
from django.views.generic import TemplateView
from itertools import groupby
from SubjectList.models import TopicalExamResults, TopicExamNotifications


class Exams(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        Group topical test by subject
    """
    template_name = 'Exams/exams.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            subject_lst = []
            student_test = StudentTest.objects.filter(user=user)
            topical_subject_count = student_test.values('subject__id')
            topics = student_test.values('topic__name').order_by('topic__name')
            topical_tests = topical_subject_count.order_by('subject__id')

            class_tests = ClassTestStudentTest.objects.filter(user=user)
            class_subject_count = class_tests.values('test__subject__id')
            my_class_tests = class_subject_count.order_by('test__subject__id')

            knec_tests = StudentKNECExams.objects.filter(user=user)
            knec_subject_count = knec_tests.values('test__subject__id')
            my_knec_test = knec_subject_count.order_by('test__subject__id')

            general_tests = GeneralTest.objects.filter(user=user)
            general_subject_count = general_tests.values('subject__id')
            my_general_tests = general_subject_count.order_by('subject__id')

            for subject_id in topical_tests:
                subject_lst.append(subject_id['subject__id'])
            for subject_id in my_general_tests:
                subject_lst.append(subject_id['subject__id'])
            for subject_id in my_class_tests:
                subject_lst.append(subject_id['test__subject__id'])
            for subject_id in my_knec_test:
                subject_lst.append(subject_id['test__subject__id'])

            # Convert the set of subject IDs to a list
            context['test_count'] = topical_subject_count.count() + knec_subject_count.count() + \
                                    class_subject_count.count() + general_subject_count.count()

            # Retrieve the Subject objects with the common subject IDs
            print(subject_lst)
            subjects = Subject.objects.filter(id__in=subject_lst)

            context['subjects'] = subjects


            return context

        except OperationalError as op_error:
            pass
        except DatabaseError as obj_error:
            pass
        return context

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class ExamTopicView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        Group topical test by topic.
    """
    template_name = 'Exams/exam_topic_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ExamTopicView, self).get_context_data(**kwargs)
        user = self.request.user
        subject_id = self.kwargs['subject']

        try:
            subject = StudentTest.objects.filter(user=user, subject=subject_id) \
                .values('topic__name', 'test_size').order_by('topic').distinct()
            context['subject'] = subject
            knec_test = StudentKNECExams.objects.filter(user=user, subject=subject_id)
            context['tests'] = knec_test
            class_test = ClassTestStudentTest.objects.filter(user=user, test__subject=subject_id).exclude(
                uuid='c2f49d23-41eb-457a-a147-8e132751774c')
            context['class_tests'] = class_test
            context['subject_name'] = self.kwargs['subject']

            return context

        except DatabaseError as error:
            pass

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class ExamSubjectDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        View tests in selected topic
    """
    template_name = 'Exams/subject_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ExamSubjectDetail, self).get_context_data(**kwargs)

        # Get subject and topic from url parameter
        subject = self.kwargs['subject']
        topic = self.kwargs['topic']

        try:
            subject = StudentTest.objects.filter(user=self.request.user, subject__name=subject, topic__name=topic)
            context['subject'] = subject

            return context

        except DatabaseError as error:
            pass

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class TestDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Exams/test_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TestDetail, self).get_context_data(**kwargs)
        user = self.request.user
        test = self.kwargs['uuid']
        instance = self.kwargs['instance']

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
            context['instance'] = instance

            return context

        except DatabaseError as error:
            pass

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class StartRepeat(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
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

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class Start(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
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
                    test = StudentTest.objects.create(user=user, subject=topic.subject, uuid=test_uuid,
                                                      topic=topic)

                    quizzes = TopicalQuizes.objects.filter(topic=topic).order_by('?')[:5]
                    test.quiz.add(*quizzes)
                    return redirect('tests', 'Topical', test.uuid)
                except:
                    return HttpResponse({'error': 'couldnt create'})



            except DatabaseError as error:
                pass

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


def get_test_instance(user, instance, test_id):
    try:
        if instance == 'Topical':
            questions = StudentTest.objects.filter(user=user, uuid=test_id).first()
            instance_type = 'StudentTest'

        elif instance == 'ClassTests':
            questions = ClassTest.objects.filter(uuid=test_id).first()
            instance_type = 'ClassTests'

        elif instance == 'General':
            questions = GeneralTest.objects.filter(user=user, uuid=test_id).first()
            instance_type = 'GeneralTest'

        elif instance == 'KNECExams':
            questions = KNECGradeExams.objects.filter(uuid=test_id).first()
            instance_type = 'KNECGradeExams'
    except DatabaseError:
        return HttpResponse({'Error': 'We encountered an error when fetching your test, please try again later while '
                                      'we fix the issue.'})

    return questions, instance_type


class Tests(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Exams/tests.html'

    def get_context_data(self, **kwargs):
        context = super(Tests, self).get_context_data(**kwargs)
        test_id = kwargs['uuid']
        instance = self.kwargs['instance']

        user = self.request.user
        question_index = self.request.session.get('index', 0)
        questions, instance_type = get_test_instance(user=user, instance=instance, test_id=test_id)
        context['test'] = questions

        if questions:
            self.request.session['test_size'] = questions.test_size
            self.request.session['instance_type'] = instance_type

            if question_index >= len(questions.quiz.all()):
                context['message'] = "Test is completed."
                return redirect('finish', instance, test_id)

            else:
                current_question = questions.quiz.all()[question_index]
                self.request.session['quiz'] = str(current_question)
                try:
                    if instance_type == 'KNECGradeExams':
                        choices = KnecQuizAnswers.objects.filter(quiz=current_question)
                    else:
                        choices = TopicalQuizAnswers.objects.filter(quiz=current_question).order_by('?')
                    context['choices'] = choices
                    context['quiz'] = current_question
                    context['index'] = question_index + 1
                    numbers = [i + 1 for i in range(len(questions.quiz.all()))]
                    context['list'] = numbers
                    context['instance'] = instance
                    context['test_id'] = test_id

                except DatabaseError as error:
                    pass
        else:
            context['error_message'] = 'We could not find this test, try again or contact us'

        return context

    def post(self, request, **kwargs):

        if request.method == 'POST':
            test_size = request.session.get('test_size')
            user = request.user
            instance = self.kwargs['instance']
            test_id = kwargs['uuid']
            selection = request.POST.get('choice')  # Get the selected choice ID from the POST data
            question_index = request.session.get('index', 0)

            test, instance_type = get_test_instance(user, instance, test_id)

            if instance_type == 'KNECGradeExams':
                quiz = KnecQuizzes.objects.filter(id=request.session['quiz']).first()
                selection = KnecQuizAnswers.objects.filter(uuid=selection).first()
                correct = KnecQuizAnswers.objects.filter(uuid=selection.uuid, is_correct=True).first()
            else:

                quiz = TopicalQuizes.objects.filter(id=request.session['quiz']).first()
                selection = TopicalQuizAnswers.objects.filter(uuid=selection).first()
                correct = selection if selection.is_correct else None
                # correct = TopicalQuizAnswers.objects.filter(uuid=selection.uuid, is_correct=True).first()

            if correct:
                if instance_type == 'ClassTests':
                    student_test = ClassTestStudentTest.objects.get(user=user, test=test)
                    student_test.marks = int(student_test.marks) + 1
                    student_test.save()
                    is_correct = True
                elif instance_type == 'KNECGradeExams':
                    student_test = StudentKNECExams.objects.get(user=user, test=test)
                    student_test.marks = int(student_test.marks) + 1
                    student_test.save()
                    is_correct = True


                else:
                    test.marks = int(test.marks) + 1
                    test.save()
                    is_correct = True

            else:
                is_correct = False

            try:
                print('created vanswer', '\n\n\n\n\n\n\n')
                if instance_type == 'KNECGradeExams':
                    test_uuid = StudentKNECExams.objects.get(user=user, test=test_id)
                    answer = StudentsKnecAnswers.objects.create(user=user, quiz=quiz,
                                                                selection=selection,
                                                                is_correct=is_correct, test=test_uuid)
                else:

                    answer = StudentsAnswers.objects.create(user=user, quiz=quiz, test_object_id=test.uuid,
                                                            selection=selection,
                                                            is_correct=is_correct)
                print(question_index, test_size, '\n\n\n\n\n\n\n')
                if question_index >= int(test_size) - 1:
                    # The exam is completed, redirect to a summary page
                    if 'index' in request.session:
                        print('\n\n\n\n\n\n\n, deleting session key')
                        del request.session['index']

                        return redirect('finish', instance, test_id)

                else:

                    request.session['index'] = question_index + 1
                    return redirect(request.path)
            except DatabaseError as error:
                return HttpResponse({'error': error})

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class Finish(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Exams/finish.html'

    def get_context_data(self, **kwargs):
        context = super(Finish, self).get_context_data(**kwargs)
        test_id = self.kwargs['uuid']
        # topic = self.kwargs['pk']
        instance = self.kwargs['instance']
        context['instance'] = instance
        user = self.request.user
        try:
            test, instance_type = get_test_instance(user, instance, test_id)
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
                                                                  message=message, subject=test.subject)
        except IntegrityError as error:
            pass


        except DatabaseError as error:
            pass

        finally:
            if instance_type == 'ClassTests':
                marks = ClassTestStudentTest.objects.get(user=user, test=test_id)
                context['score'] = marks.marks
                context['test'] = marks
                context['size'] = test.test_size
                context['instance'] = instance
            elif instance_type == 'KNECGradeExams':
                marks = StudentKNECExams.objects.get(user=user, test=test_id)
                context['score'] = marks.marks
                context['test'] = marks

                print(marks)
                context['size'] = test.test_size
                context['instance'] = instance


            else:
                context['score'] = test.marks

                context['test'] = test

            return context

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class SetTest(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Exams/set_test.html'

    def get_context_data(self, **kwargs):
        context = super(SetTest, self).get_context_data(**kwargs)
        subject = self.kwargs['subject']
        topics = Topic.objects.filter(subject__name=subject)

        context['topics'] = topics

        return context

    def post(self, request, **kwargs):
        if self.request.method == "POST":
            user = self.kwargs['mail']
            user = MyUser.objects.get(email=user)
            subject = self.kwargs['subject']
            subject = Subject.objects.filter(name=subject).first()
            topics = self.request.POST.getlist('topics')
            exam_type = self.request.POST.get('exam-type')

            test_size = self.request.POST.get('size')
            test_size = int(test_size)
            test_id = uuid.uuid4()
            date = datetime.datetime.now()

            message = 'The test you requested is now available, Good luck.'
            if exam_type == 'Topical':
                topic = Topic.objects.get(name=topics[0])
                about = f'You have a new test. View more info below.(topical){topic}'

                notification = TopicExamNotifications.objects.create(user=user, about=about,
                                                                     notification_type='retake', uuid=test_id,
                                                                     subject=subject,
                                                                     date=date,
                                                                     message=message,
                                                                     topic=topic
                                                                     )
            else:
                about = f'You have a new test. View more info below.'

                notification = TopicExamNotifications.objects.create(user=user, about=about,
                                                                     notification_type='retake',
                                                                     date=date,
                                                                     uuid=test_id,
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

            return redirect('guardian-home')

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class KNECExamView(TemplateView):
    template_name = 'Exams/knec_exam_view.html'

    def get_context_data(self, **kwargs):
        context = super(KNECExamView, self).get_context_data(**kwargs)
        grade = self.kwargs['grade']
        subjects = KNECGradeExams.objects.filter(grade=grade)

        context['subjects'] = subjects
        context['grade'] = grade
        return context


class KNECExamList(TemplateView):
    template_name = 'Exams/knec_exam_list.html'

    def get_context_data(self, **kwargs):
        context = super(KNECExamList, self).get_context_data(**kwargs)
        grade = self.kwargs['grade']
        subject = self.kwargs['subject']
        print(subject, 'se,a')
        exams = KNECGradeExams.objects.filter(grade=grade, subject__name=subject)

        context['exams'] = exams
        context['grade'] = grade
        return context


class StartKnec(TemplateView):
    template_name = 'Exams/start_knec.html'

    def get_context_data(self, **kwargs):
        context = super(StartKnec, self).get_context_data(**kwargs)
        test_uuid = self.kwargs['uuid']
        grade = self.kwargs['grade']
        test = KNECGradeExams.objects.get(uuid=test_uuid, grade=grade)

        context['test'] = test
        return context

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            user = self.request.user
            test_uuid = self.kwargs['uuid']
            grade = self.kwargs['grade']
            knec_test = KNECGradeExams.objects.get(uuid=test_uuid, grade=grade)
            subject = Subject.objects.filter(name=knec_test.subject).first()

            student_test = StudentKNECExams.objects.create(user=user, subject=subject, test=knec_test)

            return redirect('tests', 'KNECExams', test_uuid)
