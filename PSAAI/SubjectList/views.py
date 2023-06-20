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

    def post(self, request):
        if request.method == "POST":
            user = MyUser.objects.get(email=request.user)
            print(user)
            subjects = request.POST.getlist('subjects')

            # Perform operations with the selected subjects
            for subject in subjects:
                # Do something with each selected subject ID
                print(subject)
            entry = MySubjects.objects.get(user=user)

            entry.name.set(subjects)
            # logged = MyUser.objects.get(email=request.user)
            #
            # friend = MyUser.objects.get(pk=self.kwargs['pk'])
            #
            # my_list = FriendList.objects.get(user=logged)
            #
            # my_list.friends.add(friend)

            return HttpResponse(subjects)


class Learning(TemplateView):
    template_name = 'SubjecTlist\select_subject.html'

    def get_context_data(self, **kwargs):
        context = super(Learning, self).get_context_data(**kwargs)

        return context


class Read(TemplateView):
    template_name = 'SubjectList/read.html'

    def get_context_data(self, **kwargs):
        context = super(Read, self).get_context_data(**kwargs)
        grade = self.request.user.academicprofile.grade
        topic = Topic.objects.get(subject__name=self.kwargs['pk'], subject__grade=4, order=1)
        context['topic'] = topic
        context['subject'] = Subtopic.objects.filter(topic=topic)
        print(topic, '\n\n\n\n')

        return context


class Finish(TemplateView):
    template_name = 'SubjectList/finish.html'

    def get_context_data(self, **kwargs):
        context = super(Finish, self).get_context_data(**kwargs)
        subtopic = Subtopic.objects.get(name=self.kwargs['name'])

        # Access the related Topic object and its name
        topic = subtopic.topic.name

        context['topic'] = topic
        context['subtopic'] = subtopic

        return context

    def post(self, request, **kwargs):
        if request.method == 'POST':
            user = request.user
            subtopic = Subtopic.objects.get(name=self.kwargs['name'])
            topic = subtopic.topic.name
            topic = Topic.objects.get(name=topic)
            subject = subtopic.topic.subject
            about = f'{subject}: {topic} quiz is ready.'
            print('\n\n\n\n',subject,'\n\n\n\n')
            message = 'The quiz for this topic is now ready. Once started the quiz will finish in 15 minutes. Good luck.'
            is_progress = Progress.objects.filter(user=self.request.user, topic=topic)
            if  not is_progress:
                progress = Progress.objects.create(user=user, subtopic=subtopic, subject=subject)
                progress.topic.set([topic])
                notification = Notifications.objects.create(user=user, about=about, message=message, topic=topic)
            else:
                pass

        return redirect('home')


class Syllabus(TemplateView):
    template_name = 'SubjectList/syllabus.html'

    def get_context_data(self, **kwargs):
        context = super(Syllabus, self).get_context_data(**kwargs)
        print(self.kwargs['name'])
        subject = self.kwargs['name']
        context['syllabus'] = Topic.objects.filter(subject__name=subject)
        progress = Progress.objects.filter(subject__name=subject).values('topic')

        print(progress)
        progress = [item['topic'] for item in progress]
        print(progress)
        context['done'] = progress

        return context


class Messages(TemplateView):
    template_name = 'SubjectList/messages.html'

    def get_context_data(self, **kwargs):
        context = super(Messages, self).get_context_data(**kwargs)
        user = self.request.user
        messages = Notifications.objects.filter(user=user)
        context['messages'] = messages
        context['test'] = StudentTest.objects.filter(uuid__in=messages.values('uuid')).first()

        return context


class MyProgress(TemplateView):
    template_name = 'SubjectList/progress.html'

    def get_context_data(self, **kwargs):
        context = super(MyProgress, self).get_context_data(**kwargs)
        subject = Progress.objects.filter(user=self.request.user, subject__isnull=False).values('subject__name','subject__topics').annotate(topic_count=Count('topic', distinct=True))
        count = Progress.objects.filter()

        context['subject'] = subject
        return context
