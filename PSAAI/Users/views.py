from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import CreateView, DetailView, TemplateView

from SubjectList.models import MySubjects, Progress, Notifications, Topic
from Users.forms import UserRegisterForm
from Users.models import PersonalProfile


class RegisterView(CreateView):
    template_name = "Users/register.html"

    form_class = UserRegisterForm
    # success_message = "YOUR ACCOUNT HAS BEEN CREATED SUCCESSFULLY"
    def get_success_url(self):
        return reverse('login')


class MyProfile(DetailView):
    model = PersonalProfile
    template_name = "Users/profile.html"

    def get_context_data(self, **kwargs):
        context=super(MyProfile, self).get_context_data(**kwargs)
        context['subjects'] = MySubjects.objects.filter(user=self.request.user)

        return context
    def post(self, request, *args, **kwargs):
        profile=PersonalProfile.objects.get(user=self.request.user)
        fname = request.POST.get('first-name')
        new_phone_number = request.POST.get('phone_number')
        lname = request.POST.get('last-name')
        country = request.POST.get('country')
        city = request.POST.get('city')
        area = request.POST.get('area')

        # Check if the password is correct
        profile.phone = new_phone_number
        profile.f_name=fname
        profile.l_name=lname
        profile.country=country
        profile.city=city
        profile.area=area
        profile.save()

        # messages.success(request, 'Phone number updated successfully')
        return redirect(request.get_full_path())

class Home(TemplateView):
    template_name = 'Users/home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        try:
            last_subject = Progress.objects.filter(user=self.request.user).last()
            number = last_subject.topic.last().order
            context['last_subject'] = last_subject
            next_topic = Topic.objects.get(subject=last_subject.subject, order=int(number)+1)
            subject = Progress.objects.filter(user=self.request.user, subject__isnull=False).values('subject__name','subject__topics',
                                                                                                'subject__topics').annotate(
            topic_count=Count('topic', distinct=True))
            # count = Progress.objects.filter()

            context['subjects'] = subject

            context['next'] = next_topic
            unread = Notifications.objects.filter(user=self.request.user, read='False')
            context['messages'] = unread
        except:
            pass

        return context
