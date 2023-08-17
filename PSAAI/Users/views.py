from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.core.checks import messages
from django.db import DatabaseError
from django.db.models import Count
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import CreateView, DetailView, TemplateView

from SubjectList.models import MySubjects, Progress, TopicExamNotifications, Topic
from Users.forms import UserRegisterForm
from Users.models import PersonalProfile, MyUser


class RegisterView(CreateView):
    template_name = "Users/register.html"
    form_class = UserRegisterForm
    # success_message = "YOUR ACCOUNT HAS BEEN CREATED SUCCESSFULLY"
    def get_success_url(self):
        return reverse('login')


class MyProfile(LoginRequiredMixin, DetailView):
    model = PersonalProfile
    template_name = "Users/profile.html"

    def get_context_data(self, **kwargs):
        context = super(MyProfile, self).get_context_data(**kwargs)
        try:
            context['subjects'] = MySubjects.objects.filter(user=self.request.user)
            if self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            elif self.request.user.role == 'Supervisor':
                context['base_html'] = 'Supervisor/base.html'
            else:
                context['base_html'] = 'Users/base.html'

            return context

        except DatabaseError as error:
            pass

    def post(self, request, *args, **kwargs):
        if request.method == "POST":

            if 'profile' in request.POST:
                try:
                    profile = PersonalProfile.objects.get(user=self.request.user)
                    fname = request.POST.get('first-name')
                    new_phone_number = request.POST.get('phone_number')
                    lname = request.POST.get('last-name')
                    surname = request.POST.get('surname')
                    country = request.POST.get('country')
                    city = request.POST.get('city')
                    area = request.POST.get('area')

                    # Check if the password is correct
                    profile.phone1 = new_phone_number
                    profile.f_name = fname
                    profile.l_name = lname
                    profile.country = country
                    profile.surname = surname
                    profile.city = city
                    profile.area = area
                    profile.save()

                    messages.success(request, 'Phone number updated successfully')
                except PersonalProfile.DoesNotExist:
                    pass

                except PersonalProfile.MultipleObjectsReturned:
                    pass

            else:
                mail = request.POST.get('mail')
                name = request.POST.get('name')
                try:
                    # child = MyUser.objects.get(email=mail)
                    user = PersonalProfile.objects.get(user__email=mail)
                    if user.f_name == name:
                        ref_id = request.user.uuid
                        user.ref_id = ref_id
                        user.save()
                    else:
                        pass



                except MyUser.MultipleObjectsReturned:
                    return None

                except MyUser.ObjectDoesNotExist:
                    return None
            return redirect(request.get_full_path())


def loginRedirect(request):
    if request.user.role == 'Student':
        return redirect('student-home')
    elif request.user.role == 'Guardian':
        return redirect('guardian-home')
    elif request.user.role == 'Teacher':
        return redirect('teachers-home')
    elif request.user.role == 'Supervisor':
        return redirect('supervisor-home')



class Home(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Home view for the Student's dashboard.
    Displays the user's progress and related information.
    """
    template_name = 'Users/home.html'

    def get_context_data(self, **kwargs):
        """
        Populate the context with data for the template.
        """
        context = super().get_context_data(**kwargs)
        try:
            # Retrieve the user's last subject progress
            user = self.request.user
            progress_queryset = Progress.objects.filter(user=user)

            last_subject = progress_queryset.last()

            if last_subject:
                # Get the order of the last topic in the last subject
                number = last_subject.topic.last().order
                next_topic_id = int(number) + 1

                # Retrieve the next topic in the same subject
                next_topic = Topic.objects.filter(subject=last_subject.subject, order=next_topic_id).first()

                # Retrieve subjects and related information for the user
                subject = progress_queryset.filter(subject__isnull=False) \
                    .values('subject__name', 'subject__topics').annotate(topic_count=Count('topic', distinct=True))

                # Populate the context with data
                context['next'] = next_topic
                context['last_subject'] = last_subject
                context['subjects'] = subject
                context['grade']= user.academicprofile.current_class.grade

            return context

        except DatabaseError:
            # Handle database errors gracefully
            pass

    def test_func(self):
        """
        Check if the user has the required role for accessing this view.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'Student':
                return True
            else:
                return False
        else:
            return False
