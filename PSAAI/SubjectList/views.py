from datetime import date, timedelta

from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from itsdangerous import json

from Exams.models import StudentTest
from .models import *
# Create your views here.
from django.views.generic import TemplateView


class Academia(TemplateView):
    template_name = 'SubjectList/academia.html'

    def get_context_data(self, *args, **kwargs):
        context = super(Academia, self).get_context_data(**kwargs)
        context['sciences'] = Course.objects.filter(discipline='science')
        context['literature'] = Course.objects.filter(discipline='literature')
        context['social'] = Course.objects.filter(discipline='social')

        return context

    def post(self, request, **kwargs):

        if request.method == 'POST':
            subjects = request.POST.getlist('subjects')
            user = self.request.user
            try:
                my_subjects = MySubjects.objects.get(user=user)
                my_subjects.name.set(subjects)
                my_subjects.save()
                return redirect('student-home')

            except MySubjects.DoesNotExist:
                return HttpResponse(
                    'DatabaseError: We could not save your subject Selection')


class Learning(TemplateView):
    template_name = 'SubjectList/select_subject.html'


class Read(TemplateView):
    template_name = 'SubjectList/read.html'

    def get_context_data(self, **kwargs):
        context = super(Read, self).get_context_data(**kwargs)
        name = self.kwargs['name']

        try:
            context['subject'] = Subtopic.objects.get(name=name)
            return context

        except Subtopic.DoesNotExist:
            return HttpResponse('Subtopic does not exist.')

        except Subtopic.DoesNotExist:
            return HttpResponse('Subtopic does not exist.')

        except Subtopic.MultipleObjectsReturned:
            return HttpResponse('More than one Subtopic returned.')




class Finish(TemplateView):
    template_name = 'SubjectList/finish.html'

    def get_context_data(self, **kwargs):
        context = super(Finish, self).get_context_data(**kwargs)
        try:
            subtopic = Subtopic.objects.get(name=self.kwargs['name'])
            topic = subtopic.topic.name
            context['topic'] = topic
            return context

        except Subtopic.DoesNotExist:
            return HttpResponse('Subtopic does not exist.')

        except Subtopic.DoesNotExist:
            return HttpResponse('Subtopic does not exist.')

        except Subtopic.MultipleObjectsReturned:
            return HttpResponse('More than one Subtopic returned.')




    def post(self, request, **kwargs):
        if request.method == 'POST':
            user = request.user
            try:
                subtopic = Subtopic.objects.get(name=self.kwargs['name'])
                topic = subtopic.topic.name
                topic = Topic.objects.get(name=topic)
                subject = Subject.objects.get(name=subtopic.subject)
                about = f'{subject}: {topic} quiz is ready.'
                message = 'The quiz for this topic is now ready. Once started the quiz will finish in 15 minutes. Good luck.'
                is_progress = Progress.objects.filter(user=self.request.user, topic=topic, subtopic=subtopic)
                if is_progress.exists():
                    pass
                else:
                    progress = Progress.objects.create(user=user, subtopic=subtopic, subject=subject)
                    progress.topic.set([topic])
                    progress.save()
                    total_topics = topic.topics_count
                    all_subtopics = Progress.objects.filter(user=user, topic=topic).values('subtopic').distinct().count()
                    print(all_subtopics)
                    if all_subtopics == int(total_topics):
                        notification = TopicExamNotifications.objects.create(user=user, about=about, message=message,
                                                                             topic=topic)
                    else:
                        pass
            except subtopic.MultipleObjectsReturned:
                return HttpResponse('We could not save your progress, try again.')

        return redirect('student-home')


class Syllabus(TemplateView):
    template_name = 'SubjectList/syllabus.html'

    def get_context_data(self, **kwargs):
        context = super(Syllabus, self).get_context_data(**kwargs)
        subject = self.kwargs['name']
        context['syllabus'] = Topic.objects.filter(subject__name=subject).order_by('order')

        return context


class Messages(TemplateView):
    template_name = 'SubjectList/messages.html'

    def get_context_data(self, **kwargs):
        context = super(Messages, self).get_context_data(**kwargs)
        user = self.request.user
        topical_exam_results = TopicalExamResults.objects.filter(user=user)
        topical_exam = TopicExamNotifications.objects.filter(user=user)
        class_bookings = ClassBookingNotifications.objects.filter(user=user)
        subscription_notifications = SubscriptionNotifications.objects.filter(user=user)
        payment_notification = PaymentNotifications.objects.filter(user=user)

        messages = list(topical_exam) + list(topical_exam_results) + list(class_bookings) + list(
            subscription_notifications) + list(payment_notification)
        context['messages'] = messages

        return context


class MyProgress(TemplateView):
    template_name = 'SubjectList/progress.html'

    def get_context_data(self, **kwargs):
        context = super(MyProgress, self).get_context_data(**kwargs)
        subject = Progress.objects.filter(user=self.request.user, subject__isnull=False).values('subject__name',
                                                                                                'subject__topics').annotate(
            topic_count=Count('topic', distinct=True))
        count = Progress.objects.filter()

        context['subject'] = subject
        return context


class UpcomingClasses(TemplateView):
    template_name = 'SubjectList/upcoming_classes.html'

    def get_context_data(self, **kwargs):
        context = super(UpcomingClasses, self).get_context_data(**kwargs)
        today = date.today()

        # Calculate the date range for the coming 7 days
        end_date = today + timedelta(days=7)

        # Filter OnlineClass objects with a date within the
        # OnlineClass.objects.filter(date__range=(today, end_date))
        upcoming_classes = OnlineClass.objects.all()

        context['classes'] = upcoming_classes
        return context


class ClassBookings(TemplateView):
    template_name = 'SubjectList/class_booking.html'

    def get_context_data(self, **kwargs):
        context = super(ClassBookings, self).get_context_data(**kwargs)
        class_id = self.kwargs['id']
        work = OnlineClass.objects.get(id=class_id)
        context['class'] = work

        return context

    def post(self, request, **kwargs):
        user = request.user
        class_id = self.kwargs['id']
        class_instance = OnlineClass.objects.get(id=class_id)
        action = request.POST.get('action')
        if 'book-class' in action:

            booking = ClassBooking.objects.create(user=user, class_name=class_instance)
            return redirect('student-home')
        elif 'delete-class' in action:
            booking = ClassBooking.objects.filter(user=user, class_name=class_instance).first()
            print(booking)
            if booking:
                booking.delete()
            return redirect('student-home')
        else:
            return redirect('notifications')


class BookedClasses(TemplateView):
    template_name = 'SubjectList/booked_classes.html'

    def get_context_data(self, **kwargs):
        context = super(BookedClasses, self).get_context_data(**kwargs)
        bookings = ClassBooking.objects.filter(user=self.request.user)
        context['bookings'] = bookings

        return context


class CallLobby(TemplateView):
    template_name = 'SubjectList/lobby.html'

    def get_context_data(self, **kwargs):
        context = super(CallLobby, self).get_context_data(**kwargs)
        class_id = self.kwargs['id']
        class_instance = VideoChannel.objects.get(class_id=class_id)
        context['class'] = class_instance

        return context


class VideoCall(TemplateView):
    template_name = 'SubjectList/video_call.html'

    def get_context_data(self, **kwargs):
        context = super(VideoCall, self).get_context_data(**kwargs)
        app_id = 'b45a2ed7b1774731b2555d0c77264519'
        context['app_id'] = app_id

        return context
