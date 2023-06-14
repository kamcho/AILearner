from django.http import HttpResponse
from django.shortcuts import render, redirect
from itsdangerous import json

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
        my_subjects = MySubjects.objects.get(user=self.request.user)
        print(my_subjects.name)
        course_names = [course.pk for course in my_subjects.name.all()]

        # print(course_names)  # Print the names of the related courses

        # Retrieve the related Progress objects for a specific subject within MySubjects
        subject_name = "Subject Name"  # Replace with the actual subject name you want to query
        progresses = Progress.objects.filter(subject__in=course_names, user=my_subjects.user)

        # You can iterate over the progresses to access each individual progress object

        # Do something with the progress object
        # ...

        # Alternatively, you can assign the progresses to the 'progresses' context variable
        context['subjects'] = my_subjects
        context['progresses'] = progresses
        print(progresses)

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

            # Access the related Topic object and its name
            topic = subtopic.topic.name
            topic = Topic.objects.get(name=topic)
            subject = subtopic.topic.subject
            about = f'{subject}: {topic} quiz is ready.'
            message = 'The quiz for this topic is now ready. Once started the quiz will finish in 15 minutes. Good luck.'
            progress = Progress.objects.create(user=user, topic=topic, subtopic=subtopic, subject=subject)

            notification = Notifications.objects.create(user=user, about=about, message=message, topic=topic)

        return redirect('home')


class Syllabus(TemplateView):
    template_name = 'SubjectList/syllabus.html'

    def get_context_data(self, **kwargs):
        context = super(Syllabus, self).get_context_data(**kwargs)
        print(self.kwargs['name'])
        context['syllabus'] = Topic.objects.filter(subject__name=self.kwargs['name'], subject__grade=1)

        return context


class Messages(TemplateView):
    template_name = 'SubjectList/messages.html'

    def get_context_data(self, **kwargs):
        context = super(Messages, self).get_context_data(**kwargs)
        user = self.request.user
        context['messages'] = Notifications.objects.filter(user=user)

        return context
