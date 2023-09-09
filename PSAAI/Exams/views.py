import datetime
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import DatabaseError, IntegrityError
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import *
from django.views.generic import TemplateView
from SubjectList.models import TopicalExamResults, TopicExamNotifications

logger = logging.getLogger('django')


class Exams(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Group topical test by subject.
    """
    template_name = 'Exams/exams.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display user's exams grouped by subject.

        This method fetches the user's exams, groups them by subject, and displays the subjects in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            # Lists to store subject IDs
            subject_ids = []

            # Retrieve student test data
            student_tests = StudentTest.objects.filter(user=user)
            topical_subject_counts = student_tests.values('subject__id')
            topical_tests = topical_subject_counts.order_by('subject__id')

            # Retrieve class test data
            class_tests = ClassTestStudentTest.objects.filter(user=user)
            class_subject_counts = class_tests.values('test__subject__id')
            my_class_tests = class_subject_counts.order_by('test__subject__id')

            # Retrieve KNEC test data
            knec_tests = StudentKNECExams.objects.filter(user=user)
            knec_subject_counts = knec_tests.values('test__subject__id')
            my_knec_tests = knec_subject_counts.order_by('test__subject__id')

            # Retrieve general test data
            general_tests = GeneralTest.objects.filter(user=user)
            general_subject_counts = general_tests.values('subject__id')
            my_general_tests = general_subject_counts.order_by('subject__id')

            # Collect subject IDs from different types of tests
            if topical_tests:
                for subject_id in topical_tests:
                    subject_ids.append(subject_id['subject__id'])

            if my_general_tests:
                for subject_id in my_general_tests:
                    subject_ids.append(subject_id['subject__id'])

            if my_class_tests:
                for subject_id in my_class_tests:
                    subject_ids.append(subject_id['test__subject__id'])

            if my_knec_tests:
                for subject_id in my_knec_tests:
                    subject_ids.append(subject_id['test__subject__id'])
            # Convert the list of subject IDs to a set to remove duplicates
            subject_ids_set = set(subject_ids)

            # Count the total number of tests
            total_tests_count = (
                    topical_subject_counts.count() +
                    knec_subject_counts.count() +
                    class_subject_counts.count() +
                    general_subject_counts.count()
            )

            # Retrieve the Subject objects with the common subject IDs
            subjects = Subject.objects.filter(id__in=subject_ids_set)

            context['test_count'] = total_tests_count
            context['subjects'] = subjects


        except Exception as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': uuid.uuid4(),
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context

    def test_func(self):
        user = self.request.user

        return user.role == "Student"


class ExamTopicView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Group topical test by topic.
    """
    template_name = 'Exams/exam_topic_detail.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display exams grouped by topic for a specific subject.

        This method fetches the user's exams for a specific subject, groups them by topic, and displays the topics
        in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(ExamTopicView, self).get_context_data(**kwargs)
        user = self.request.user
        subject_id = self.kwargs['subject']

        try:
            # Retrieve student test data for the subject
            subject_tests = StudentTest.objects.filter(user=user, subject__id=subject_id) \
                .values('topic__name').order_by('topic').distinct()

            # Retrieve KNEC test data for the subject
            knec_tests = StudentKNECExams.objects.filter(user=user, subject__id=subject_id)

            # Retrieve class test data for the subject, excluding a specific UUID
            class_tests = ClassTestStudentTest.objects.filter(user=user, test__subject__id=subject_id)

            context['subject'] = subject_tests
            context['tests'] = knec_tests
            context['class_tests'] = class_tests
            context['subject_name'] = self.kwargs['subject']
            if not (subject_tests or knec_tests or class_tests):
                messages.info(self.request, 'We could not find results matching your query.')

        except DatabaseError as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')

            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': uuid.uuid4(),
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context

    def test_func(self):
        user = self.request.user

        return user.role == "Student"


class ExamSubjectDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    View tests in the selected topic.
    """
    template_name = 'Exams/subject_detail.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display tests for a selected subject and topic.

        This method fetches the user's tests for a specific subject and topic, and displays them in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(ExamSubjectDetail, self).get_context_data(**kwargs)

        # Get subject and topic from URL parameters
        subject_id = self.kwargs['subject']
        topic_name = self.kwargs['topic']

        try:
            # Retrieve tests for the selected subject and topic
            tests = StudentTest.objects.filter(
                user=self.request.user,
                subject__id=subject_id,
                topic__name=topic_name
            )

            context['subject'] = tests
            if not tests:
                messages.info(self.request, 'We could not find results matching your query.')

        except DatabaseError as e:
            # Handle DatabaseError if needed
            messages.error(self.request, 'An error occurred. We are fixing it!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': uuid.uuid4(),
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context

    def test_func(self):
        user = self.request.user

        return user.role == "Student"


class TestDetail(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Exams/test_detail.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display details of a specific test for the user.

        This method fetches details of a specific test (based on the instance) for the user and displays them in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(TestDetail, self).get_context_data(**kwargs)
        user = self.request.user
        test_uuid = self.kwargs['uuid']
        instance = self.kwargs['instance']
        try:
            test_uuid = uuid.UUID(test_uuid)  # Convert the string to a UUID object
            if instance == 'Topical':

                model = 'StudentTest'
                answers = StudentsAnswers.objects.filter(user=user, test_object_id=test_uuid)
                test = StudentTest.objects.get(user=user, uuid=test_uuid)

            elif instance == 'KNECExams':

                model = 'StudentKNECExams'
                test = StudentKNECExams.objects.get(user=user, test=test_uuid)
                answers = StudentsKnecAnswers.objects.filter(user=user, test=test)

            elif instance == 'ClassTests':

                model = 'ClassTestStudentTest'
                answers = StudentsAnswers.objects.filter(user=user, test_object_id=test_uuid)
                test = ClassTestStudentTest.objects.get(user=user, test=test_uuid)

            else:
                pass

            context['quizzes'] = answers
            context['marks'] = test
            context['instance'] = instance

        except ValueError:
            # Handle invalid UUID format
            messages.error(self.request, 'Invalid UUID format. Please do not edit the url !!.')

        except ObjectDoesNotExist as e:
            messages.error(self.request, 'We could not find the test!. please contact @support')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': uuid.uuid4(),
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': model,

                }
            )





        except DatabaseError as e:
            messages.error(self.request, 'An error occurred!!. Do not be alarmed we are fixing it.')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': uuid.uuid4(),
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )
        # Set the base HTML template based on user role
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        else:
            context['base_html'] = 'Users/base.html'
        if not answers:
            messages.error(self.request, 'Dear user we could not retrieve your tests detail.Please contact @support')

        return context

    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


class Start(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Exams/start.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and display details of the starting point for an exam.

        This method fetches details of a starting point for an exam (based on the topic name) and displays them in the template.

        Args:
            **kwargs: Additional keyword arguments from the URL.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(Start, self).get_context_data(**kwargs)

        try:
            topic_name = self.kwargs['topic']
            test_id = kwargs['uuid']
            user = self.request.user


            # Retrieve the topic based on the 'pk' parameter from the URL
            topics = Topic.objects.get(name=topic_name)
            test = StudentTest.objects.filter(user=user, uuid=test_id)
            print(test, topics)
            if test:
                context['done'] = 'True'
                messages.info(self.request, 'This test has already been done and cannot be retaken.')

            # Check if topic is None (no object found)

            context['topic'] = topics

        except Topic.DoesNotExist as e:
            # Handle the case where no object is found
            context['topic'] = None
            messages.error(self.request, 'An error occurred !!! Dear Student do not edit the url !!')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': uuid.uuid4(),
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'Topic',

                }
            )

        except Exception as e:
            # Handle other DatabaseError if needed
            messages.error(self.request, 'An error occurred !!! We are fixing it. '
                                         'If the problem persists contact @support')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.critical(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': uuid.uuid4(),
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Critical',
                    'model': 'DatabaseError',

                }
            )

        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            user = request.user
            test_uuid = kwargs['uuid']
            topic_name = kwargs['topic']

            try:
                # Retrieve the topic based on the 'pk' parameter from the URL
                topic = Topic.objects.get(name=topic_name)

                print(topic)

                # Create a new StudentTest object
                test = StudentTest.objects.create(
                    user=user,
                    subject=topic.subject,
                    uuid=test_uuid,
                    topic=topic
                )

                # Retrieve and add a set of quizzes to the test
                quizzes = TopicalQuizes.objects.filter(topic=topic).order_by('?')[:5]
                test.quiz.add(*quizzes)

                # Redirect to the 'tests' view with appropriate arguments
                return redirect('tests', 'Topical', test.uuid)

            except IntegrityError as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred and therefore, you cannot take this test at this time!!.'
                                             ' Stand by as we fix the issue. Sorry for any inconveniences caused!!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': uuid.uuid4(),
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'StudentTest',

                    }
                )

            except Exception as e:
                # Handle DatabaseError if needed
                messages.error(self.request, 'An error occurred and therefore, you cannot take this test at this time!!.'
                                             ' Stand by as we fix the issue. Sorry for any inconveniences caused!!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.critical(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': uuid.uuid4(),
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Critical',
                        'model': 'DatabaseError',

                    }
                )
            return redirect(request.get_full_path())


    def test_func(self):
        user = self.request.user
        if user.role == "Student":
            return True
        else:
            return False


def get_test_instance(user, instance, test_id):
    try:
        if instance == 'Topical':
            questions = StudentTest.objects.get(user=user, uuid=test_id)
            instance_type = 'StudentTest'

        elif instance == 'ClassTests':
            questions = ClassTest.objects.get(uuid=test_id)
            instance_type = 'ClassTests'

        elif instance == 'General':
            questions = GeneralTest.objects.get(user=user, uuid=test_id)
            instance_type = 'GeneralTest'

        elif instance == 'KNECExams':
            questions = KNECGradeExams.objects.get(uuid=test_id)
            instance_type = 'KNECGradeExams'

        return questions, instance_type

    except MultipleObjectsReturned:
        raise MultipleObjectsReturned

    except ObjectDoesNotExist:
        raise ObjectDoesNotExist  # Return None for both questions and instance_type if the object does not exist

    except DatabaseError:
        raise DatabaseError


class Tests(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'Exams/tests.html'

    def get_context_data(self, **kwargs):
        context = super(Tests, self).get_context_data(**kwargs)
        test_id = kwargs['uuid']
        instance = self.kwargs['instance']

        user = self.request.user
        question_index = self.request.session.get('index', 0)
        try:
            questions, instance_type = get_test_instance(user=user, instance=instance, test_id=test_id)
            context['test'] = questions
            if questions:
                self.request.session['test_size'] = questions.test_size
                self.request.session['instance_type'] = instance_type

                if question_index >= len(questions.quiz.all()):
                    context['message'] = "Test is completed."

                else:
                    current_question = questions.quiz.all()[question_index]
                    self.request.session['quiz'] = str(current_question)

                    if instance_type == 'KNECGradeExams':
                        choices = KnecQuizAnswers.objects.filter(quiz=current_question)

                    else:
                        choices = TopicalQuizAnswers.objects.filter(quiz=current_question).order_by('?')
                    correct_choice = choices.filter(is_correct=True)
                    if choices.count() <= 4 or correct_choice is None:
                        messages.error(self.user, 'This test is not complete try it later')
                        context['invalidate'] = True
                    else:
                        context['choices'] = choices
                        context['quiz'] = current_question
                        context['index'] = question_index + 1
                        numbers = [i + 1 for i in range(len(questions.quiz.all()))]
                        context['list'] = numbers
                        context['instance'] = instance

                        context['test_id'] = test_id

        except MultipleObjectsReturned:
            messages.error(self.request, 'Multiple Tests were returned !! we are fixin it')
        except ObjectDoesNotExist:
            messages.error(self.request, 'Test not found try again or contact admin!!')
        except DatabaseError:
            messages.error(self.request, 'Database Error ! Try again later!!')
        except (Exception,):
            messages.error(self.request, 'An exception occured and we are fixing it!!')

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
    """
    View for setting a test for a specific subject.
    """
    template_name = 'Exams/set_test.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the set test page.

        Args:
            **kwargs: Keyword arguments from the URL, including 'subject'.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(SetTest, self).get_context_data(**kwargs)
        subject = self.kwargs['subject']

        try:
            # Attempt to retrieve topics related to the specified subject
            topics = Topic.objects.filter(subject__name=subject)

            context['topics'] = topics

        except Exception as e:
            # Handle any exceptions that may occur
            messages.error(self.request, 'An error occurred while fetching topics for the test. Please try again.')

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
    """
    View for displaying KNEC exams for a specific grade.
    """
    template_name = 'Exams/knec_exam_view.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the KNEC exam view page.

        Args:
            **kwargs: Keyword arguments from the URL, including 'grade'.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(KNECExamView, self).get_context_data(**kwargs)
        grade = self.kwargs['grade']

        try:
            # Attempt to retrieve the subjects for the specified grade
            subjects = KNECGradeExams.objects.filter(grade=grade)

            context['subjects'] = subjects
            context['grade'] = grade

        except Exception as e:
            # Handle any exceptions that may occur
            messages.error(self.request, 'An error occurred while fetching KNEC exams. Please try again.')

        return context


class KNECExamList(TemplateView):
    """
    View for listing KNEC exams for a specific grade and subject.
    """
    template_name = 'Exams/knec_exam_list.html'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the KNEC exam list page.

        Args:
            **kwargs: Keyword arguments from the URL, including 'grade' and 'subject'.

        Returns:
            dict: A dictionary containing context data for the template.
        """
        context = super(KNECExamList, self).get_context_data(**kwargs)
        grade = self.kwargs['grade']
        subject = self.kwargs['subject']

        try:
            # Attempt to retrieve the KNEC exams for the specified grade and subject
            exams = KNECGradeExams.objects.filter(grade=grade, subject__name=subject)

            context['exams'] = exams
            context['grade'] = grade

        except Exception as e:
            # Handle any exceptions that may occur
            messages.error(self.request, 'An error occurred while fetching KNEC exams. Please try again.')

        return context


class StartKnec(TemplateView):
    """
    View for starting a KNEC exam.
    """
    template_name = 'Exams/start_knec.html'

    def get_context_data(self, **kwargs):
        """
        Retrieve and prepare context data for rendering the exam start page.

        Args:
            **kwargs: Keyword arguments from the URL, including 'uuid' and 'grade'.

        Returns:
            dict: Context data for rendering the template.
        """
        context = super(StartKnec, self).get_context_data(**kwargs)
        test_uuid = self.kwargs['uuid']
        grade = self.kwargs['grade']

        try:
            # Attempt to retrieve the KNEC exam based on UUID and grade
            test = KNECGradeExams.objects.get(uuid=test_uuid, grade=grade)
        except KNECGradeExams.DoesNotExist:
            # Handle the case where no matching exam is found
            test = None
            messages.error(self.request, 'We could not find this test. Contact admin')
        except MultipleObjectsReturned:
            # Handle the case where multiple matching exam is found

            test = None
            messages.error(self.request, 'There was an issue retrieving this test were fixing it')
        except (DatabaseError, Exception):
            test = None
            messages.error(self.request, 'Server problems were fixing it')

        context['test'] = test
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle the POST request to start a KNEC exam.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Keyword arguments from the URL, including 'uuid' and 'grade'.

        Returns:
            HttpResponseRedirect: Redirects to the appropriate exam page.
        """
        if request.method == "POST":
            user = self.request.user
            test_uuid = self.kwargs['uuid']

            try:
                # Attempt to retrieve the KNEC exam based on UUID and grade
                knec_test = self.get_context_data().get('test')
                subject = Subject.objects.get(id=knec_test.subject.id)

                # Create a StudentKNECExams object for the user
                student_test = StudentKNECExams.objects.create(user=user, subject=subject, test=knec_test)

                # Redirect to the KNEC exam page
                return redirect('tests', 'KNECExams', test_uuid)


            except Subject.DoesNotExist:
                # Handle no subject found
                messages.error(request, 'Subject does not exist!!')
            except MultipleObjectsReturned:
                # Handle multiple subject found
                messages.error(request, 'multiple subjects returned')

        return redirect(request.get_full_path())
        # Redirect to the appropriate page on error
