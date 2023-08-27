import datetime
from datetime import date, timedelta

import requests
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError, DatabaseError
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from itsdangerous import json

from Exams.models import StudentTest, TopicalQuizAnswers, StudentsAnswers, TopicalQuizes, ClassTest, ClassTestStudentTest
from Teacher.models import ClassTestNotifications
from .models import *
# Create your views here.
from django.views.generic import TemplateView


class Academia(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/academia.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Academia, self).get_context_data(**kwargs)

        try:
            context['sciences'] = Course.objects.filter(discipline='science')
            context['literature'] = Course.objects.filter(discipline='literature')
            context['social'] = Course.objects.filter(discipline='social')

        except DatabaseError as error:
            context['error_message'] = "Failed to retrieve data from the database. Please try again later."
        return context

    def post(self, request, **kwargs):

        if request.method == 'POST':
            subjects = request.POST.getlist('subjects')
            user = self.request.user
            try:
                my_subjects = MySubjects.objects.filter(user=user).first()
                my_subjects.name.set(subjects)
                my_subjects.save()

                return redirect('student-home')

            except DatabaseError as error:
                return redirect('student-home')


class Learning(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/select_subject.html'


class Read(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/read.html'

    def get_context_data(self, **kwargs):
        context = super(Read, self).get_context_data(**kwargs)
        name = self.kwargs['name']

        try:
            context['subject'] = Subtopic.objects.filter(name=name).first()
            return context

        except DatabaseError as error:
            pass



class Finish(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/finish.html'

    def get_context_data(self, **kwargs):
        context = super(Finish, self).get_context_data(**kwargs)
        try:
            subtopic = Subtopic.objects.filter(name=self.kwargs['name']).first()
            topic = subtopic.topic.name
            context['topic'] = topic

            return context

        except DatabaseError as error:
            pass

    def post(self, request, **kwargs):
        if request.method == 'POST':
            user = request.user
            try:
                subtopic = Subtopic.objects.filter(name=self.kwargs['name']).first()
                topic = subtopic.topic.name
                topic = Topic.objects.filter(name=topic).first()
                subject = Subject.objects.filter(name=subtopic.subject).first()
                about = f'{subject}: {topic} quiz is ready.'
                message = 'The quiz for this topic is now ready. Once started the quiz will finish in 15 minutes. Good luck.'
                is_progress = Progress.objects.filter(user=self.request.user, topic=topic, subtopic=subtopic)
                print(subtopic, topic, subject, is_progress)
                if is_progress:
                    pass
                else:
                    try:
                        progress = Progress.objects.create(user=user, subtopic=subtopic, subject=subject)
                        progress.topic.set([topic])
                        progress.save()
                    except IntegrityError:
                        pass
                    total_topics = topic.topics_count
                    all_subtopics = Progress.objects.filter(user=user, topic=topic).values(
                        'subtopic').distinct().count()
                    print(all_subtopics)
                    if all_subtopics == int(total_topics):
                        try:
                            notification = TopicExamNotifications.objects.create(user=user, about=about,
                                                                                 notification_type='quiz',
                                                                                 subject=subject, message=message,
                                                                                 topic=topic,
                                                                                 date = datetime.datetime.now())
                        except :
                            return HttpResponse(f'We could not create a test for you . Please contact Admin.')
                    else:
                        pass

            except DatabaseError as error:
                pass

            except Exception as error:
                return HttpResponse(f'{error}')

        return redirect('student-home')


class Syllabus(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/syllabus.html'

    def get_context_data(self, **kwargs):
        context = super(Syllabus, self).get_context_data(**kwargs)
        subject = self.kwargs['name']
        try:
            context['syllabus'] = Topic.objects.filter(subject__name=subject).order_by('order')


        except DatabaseError as error:
            pass

        return context


class Assignment(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/assignment.html'

    def get_context_data(self, **kwargs):
        context = super(Assignment, self).get_context_data(**kwargs)
        current_class = self.request.user.academicprofile.current_class
        assignments = ClassTest.objects.filter(class_id=current_class)
        context['assignments'] = assignments

        return context


class AssignmentDetail(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/assignment_lobby.html'

    def get_context_data(self, **kwargs):
        context = super(AssignmentDetail, self).get_context_data(**kwargs)
        test_uuid = self.kwargs['uuid']
        test = ClassTest.objects.filter(uuid=test_uuid).first()
        context['assignment'] = test

        return context

    def post(self, request, **kwargs):
        if request.method == "POST":
            user = request.user
            test = self.kwargs['uuid']
            class_test = ClassTest.objects.filter(uuid=test).first()
            save_test = ClassTestStudentTest.objects.create(user=user, test=class_test, finished=False)

            return redirect('tests', 'ClassTests', test)


class TakeAssessment(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/assessment.html'

    def get_context_data(self, **kwargs):
        context = super(TakeAssessment, self).get_context_data(**kwargs)

        test_id = self.kwargs['uuid']
        class_test = ClassTest.objects.filter(uuid=test_id).first()
        # del self.request.session['class_test_quiz_index']
        index = self.request.session.get('class_test_quiz_index', 0)
        test_size = class_test.test_size
        current_quiz = class_test.quiz.all()[index]
        self.request.session['quiz'] = str(current_quiz)
        self.request.session['test_size'] = test_size
        context['quiz'] = current_quiz
        context['index'] = index+1
        numbers = [i + 1 for i in range(test_size)]
        choices = TopicalQuizAnswers.objects.filter(quiz=current_quiz)
        context['choices'] = choices

        context['test_size'] = numbers

        return context

    def post(self, request, **kwargs):
        user = request.user
        test = self.kwargs['uuid']
        selection = request.POST.get('choice')
        quiz = request.session.get('quiz')
        index = self.request.session.get('class_test_quiz_index', 0)
        test_size = request.session['test_size']
        quiz = TopicalQuizes.objects.filter(id=quiz).first()
        selection = TopicalQuizAnswers.objects.get(uuid=selection)
        test = ClassTest.objects.filter(uuid=test).first()

        answer = StudentsAnswers.objects.create(user=user, quiz=quiz, selection=selection, test=test)

        if int(index) >= int(test_size - 1):
            del self.request.session['class_test_quiz_index']
            del self.request.session['test_size']
            del self.request.session['quiz']

            return redirect('finish-assessment', self.kwargs['uuid'])
        else:
            request.session['class_test_quiz_index'] = index + 1

            return redirect(request.path, test)


class FinishAssessment(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/finish_assessment.html'

    def get_context_data(self, **kwargs):
        test = self.kwargs['uuid']

        context = super(FinishAssessment, self).get_context_data(**kwargs)
        user = self.request.user
        class_test = ClassTest.objects.filter(uuid=test).first()
        context['test_size']= class_test.test_size
        try:
            test = ClassTestStudentTest.objects.filter(user=user, test=test).order_by('date').last()
            # subject = test.test.subject
            # subject = Subject.objects.filter(name=subject).first()
            # print(subject,'\n\n\n\n')
            # print(test.uuid, '\n\n\n\n\n')
            if test:
                answers = StudentsAnswers.objects.filter(user=user, test=class_test).values('selection__uuid')
                correct_answers = TopicalQuizAnswers.objects.filter(uuid__in=answers, is_correct='True')
                print(correct_answers, '\n\n\n')
                test.marks = correct_answers.count()
                test.save()
                mark = StudentsAnswers.objects.filter(selection__in=correct_answers)
                for item in mark:
                    item.is_correct = True
                    item.save()
                # about = f'The results for {subject} class test  are out.'
                # message = f'Congratulations on completing your test. The results' \
                #           ' are out, click the button below to view the results. '
                #
                #
                # try:
                #     notifications = TopicalExamResults.objects.create(user=user, test=test.uuid, about=about, message=message,  subject=subject)
                #
                # except IntegrityError as error:
                #     pass
                context['score'] = correct_answers.count()
                context['test'] = class_test
            else:
                pass

            return context

        except DatabaseError as error:
            pass


class Messages(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/messages.html'

    def get_context_data(self, **kwargs):
        context = super(Messages, self).get_context_data(**kwargs)
        user = self.request.user
        if self.request.user.role == 'Guardian':
            context['base_html'] = 'Guardian/baseg.html'
        elif self.request.user.role == 'Teacher':
            context['base_html'] = 'Teacher/teachers_base.html'
        else:
            context['base_html'] = 'Users/base.html'
        if user.role == "Student":
            class_id = user.academicprofile.current_class
            try:
                topical_exam_results = TopicalExamResults.objects.filter(user=user)
                topical_exam = TopicExamNotifications.objects.filter(user=user)
                class_bookings = ClassBookingNotifications.objects.filter(user=user)
                class_test_notifications = ClassTestNotifications.objects.filter(class_id=class_id)
                messages = list(topical_exam) + list(topical_exam_results) + list(class_bookings) + list(class_test_notifications)
                context['messages'] = messages


                return context


            except DatabaseError as error:
                pass

        else:
            payment_notification = PaymentNotifications.objects.filter(user=user)
            subscription_notifications = SubscriptionNotifications.objects.filter(user=user)
            messages = list(subscription_notifications) + list(payment_notification)

            context['messages'] = messages
            return context


class MyProgress(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/progress.html'

    def get_context_data(self, **kwargs):
        context = super(MyProgress, self).get_context_data(**kwargs)
        try:
            subject = Progress.objects.filter(user=self.request.user,
                                              subject__isnull=False).values('subject__name', 'subject__topics'). \
                annotate(topic_count=Count('topic', distinct=True))

            context['subject'] = subject
            return context

        except DatabaseError as error:
            pass


class UpcomingClasses(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/upcoming_classes.html'

    def get_context_data(self, **kwargs):
        context = super(UpcomingClasses, self).get_context_data(**kwargs)
        today = date.today()

        # Calculate the date range for the coming 7 days
        end_date = today + timedelta(days=7)

        # Filter OnlineClass objects with a date within the
        try:
            # OnlineClass.objects.filter(date__range=(today, end_date))
            upcoming_classes = OnlineClass.objects.all()

            context['classes'] = upcoming_classes
            return context

        except DatabaseError as error:
            pass


class ClassBookings(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/class_booking.html'

    def get_context_data(self, **kwargs):
        context = super(ClassBookings, self).get_context_data(**kwargs)
        class_id = self.kwargs['id']

        try:
            work = OnlineClass.objects.filter(id=class_id).last()
            context['class'] = work
            return context

        except DatabaseError as error:
            pass

    def post(self, request, **kwargs):
        user = request.user
        class_id = self.kwargs['id']
        try:

            class_instance = OnlineClass.objects.filter(id=class_id).last()
            action = request.POST.get('action')
            if class_instance:
                if 'book-class' in action:

                    try:
                        booking = ClassBooking.objects.create(user=user, class_name=class_instance)
                        return redirect('student-home')
                    except IntegrityError:
                        pass
                elif 'delete-class' in action:
                    booking = ClassBooking.objects.filter(user=user, class_name=class_instance).first()
                    print(booking)
                    if booking:
                        booking.delete()
                    return redirect('student-home')
                else:
                    return redirect('notifications')

        except DatabaseError as error:
            pass


class BookedClasses(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/booked_classes.html'

    def get_context_data(self, **kwargs):
        context = super(BookedClasses, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            bookings = ClassBooking.objects.filter(user=user)
            context['bookings'] = bookings

            return context

        except DatabaseError as error:
            pass


class CallLobby(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/lobby.html'

    def get_context_data(self, **kwargs):
        context = super(CallLobby, self).get_context_data(**kwargs)
        class_id = self.kwargs['id']
        try:
            class_instance = VideoChannel.objects.filter(class_id=class_id).last()
            context['class'] = class_instance

            return context

        except DatabaseError as error:
            pass


class VideoCall(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/video_call.html'

    def get_context_data(self, **kwargs):
        context = super(VideoCall, self).get_context_data(**kwargs)
        app_id = 'b45a2ed7b1774731b2555d0c77264519'
        context['app_id'] = app_id

        return context


class ContactUs(LoginRequiredMixin, TemplateView):
    template_name = 'SubjectList/contact.html'

    def get_context_data(self, **kwargs):
        context = super(ContactUs, self).get_context_data(**kwargs)

        try:
            subject = Course.objects.all()
            context['subject'] = subject

            return context

        except DatabaseError as error:
            pass

    def post(self, request, **kwargs):

        if request.method == 'POST':
            user = request.user
            message = request.POST.get('message')
            about = request.POST.get('about')

            if about == 'Academic':
                subject = request.POST.get('subject')

                try:
                    subject = Subject.objects.filter(name=subject).first()
                    try:

                        inquiry = AcademicInquiries.objects.create(user=user, quiz_class=about, subject=subject,
                                                               message=message)
                        return redirect('student-home')

                    except IntegrityError:
                        pass

                except DatabaseError as error:
                    pass

            elif about == 'Account':
                try:
                    inquiry = AccountInquiries.objects.create(user=user, quiz_class=about, message=message)

                    return redirect('student-home')

                except IntegrityError:
                    pass
            else:
                return HttpResponse('could not send your inquiry. Please try again')





