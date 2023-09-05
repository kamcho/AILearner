from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import DatabaseError
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, TemplateView
from SubjectList.models import Progress, Topic, Subject
from Users.forms import UserRegisterForm
from Users.models import PersonalProfile


class RegisterView(CreateView):
    template_name = "Users/register.html"
    form_class = UserRegisterForm

    def get_success_url(self):
        return reverse('login')


class MyProfile(LoginRequiredMixin, TemplateView):
    """
        view and manipulate a user's profile.
        Attach a learner to your watch list for parents/guardians
    """
    template_name = "Users/profile.html"

    def get_context_data(self, **kwargs):
        context = super(MyProfile, self).get_context_data(**kwargs)
        try:
            # Check user's role and use appropriate base Html Template
            if self.request.user.role == 'Student':
                # get the current logged in user(learner) current grade and associated Subjects
                grade = self.request.user.academicprofile.current_class.grade
                subjects = Subject.objects.filter(grade=grade)
                context['subjects'] = subjects
                context['base_html'] = 'Users/base.html'
            elif self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            elif self.request.user.role == 'Supervisor':
                context['base_html'] = 'Supervisor/base.html'
            else:
                # If logged in user's role doesn't match any criteria log out the user and show message
                messages.error(self.request, 'You are not authorised to use this system!')
                redirect('logout')

            return context

        except DatabaseError:
            pass

    def post(self, args, **kwargs):
        # Check for Post requests
        if self.request.method == "POST":
            user = self.request.user
            # Check which button is clicked
            if 'profile' in self.request.POST:
                try:
                    # Get logged in user's profile for editing
                    profile = PersonalProfile.objects.get(user=user)
                    f_name = self.request.POST.get('first-name')
                    new_phone_number = self.request.POST.get('phone-number')
                    l_name = self.request.POST.get('last-name')
                    surname = self.request.POST.get('surname')
                    city = self.request.POST.get('city')
                    profile.phone = new_phone_number
                    profile.f_name = f_name
                    profile.l_name = l_name
                    profile.surname = surname
                    profile.city = city
                    profile.save()
                    messages.success(self.request, 'Profile has been successfully Updated!')

                    return redirect(self.request.get_full_path())


                except PersonalProfile.DoesNotExist:
                    pass

                except PersonalProfile.MultipleObjectsReturned:
                    pass

                except DatabaseError:
                    # Show error message in case of any unhandled database error
                    messages.error(self.request, 'Sorry, there was an issue updating your profile. Please try again.')
                    return redirect(self.request.get_full_path())

            # Add a learner to a guardians watch list
            elif 'attachment' in self.request.POST:
                if user.role == 'Guardian':
                    mail = self.request.POST.get('mail')
                    name = self.request.POST.get('name')
                    try:
                        learner = PersonalProfile.objects.get(user__email=mail)  # get users profile
                        # Ensure users first name matches the value of first name and ensure that the user is a student.
                        if learner.f_name == name and learner.role == 'Student':
                            ref_id = self.request.user.uuid
                            learner.ref_id = ref_id
                            learner.save()
                        elif learner.f_name == name and learner.role != 'Student':
                            messages.error(self.request, 'You can only add a student to your watch list')
                        elif learner.f_name != name:
                            messages.error(self.request, 'Sorry, we could not find a User matching your search!!')
                        else:
                            messages.error(self.request, 'Sorry, we could not process your request!!')

                        return redirect(self.request.get_full_path())




                    except PersonalProfile.MultipleObjectsReturned:
                        return None

                    except PersonalProfile.ObjectDoesNotExist:
                        return None
                else:
                    messages.error(self.request, 'Sorry, You are not authorised to perform this action.')

            else:
                # Handle unknown button clicks
                messages.error(self.request, 'Sorry, we could not process your request. Please contact Admin!')

                return redirect(self.request.get_full_path())


class LoginRedirect(LoginRequiredMixin, TemplateView):
    """
        Redirect a user based on their role
    """
    template_name = 'Users/login_redirect.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        role = self.request.user.role

        # If a user has not updated their profile redirect them to profile editing page
        if self.request.user.personalprofile.f_name == '':
            return redirect('edit-profile')
        else:
            if role == 'Student':
                return redirect('student-home')
            elif role == 'Guardian':
                return redirect('guardian-home')
            elif role == 'Teacher':
                return redirect('teachers-home')
            elif role == 'Supervisor':
                return redirect('supervisor-home')
            else:
                messages.error('You are not authorised to use this system, Contact Admin!!')
                return redirect('logout')


def finish_profile_setup(user, f_name, l_name, surname, phone):
    profile = PersonalProfile.objects.get(user=user)

    profile.f_name = f_name
    profile.l_name = l_name
    if phone:
        profile.phone = phone
    profile.surname = surname
    profile.save()
    return None


class FinishSetup(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
        User's profile edit Page, mainly for first time account users
    """
    template_name = 'Users/edit_profile.html'

    def post(self, request, **kwargs):
        if request.method == 'POST':
            f_name = request.POST.get('f_name')
            l_name = request.POST.get('l_name')
            surname = request.POST.get('surname')
            phone = request.POST.get('phone')
            user = self.request.user  # get user from session.

            try:
                # Get user's profile for editing
                finish_profile_setup(user=user, f_name=f_name, l_name=l_name, surname=surname, phone=phone)


            # Handle errors related to multiple profiles returned
            except PersonalProfile.MultipleObjectsReturned:
                return None
            # if no profile matching query is found, create it and update it
            except PersonalProfile.ObjectDoesNotExist:
                PersonalProfile.objects.create(user=user)
                finish_profile_setup(user=user, f_name=f_name, l_name=l_name, surname=surname, phone=phone)


            except DatabaseError:
                messages.error(request, 'We could not process your request, try again.!!')
                return redirect(request.get_full_path())

            # Finally reroute a user based on their role
            finally:

                if request.user.role == 'Student':
                    return redirect('student-home')
                elif request.user.role == 'Guardian':
                    return redirect('guardian-home')
                elif request.user.role == 'Teacher':
                    return redirect('teachers-home')
                elif request.user.role == 'Supervisor':
                    return redirect('supervisor-home')

        else:
            return redirect(request.get_full_path())

    # ensure a user is only editing their profile.
    def test_func(self):
        user = self.request.user
        profile = get_object_or_404(PersonalProfile, user=user)
        messages.error(self.request, 'You can only edit your Profile.!!!')
        return profile.user == user  # Check if the profile belongs to the logged-in user


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
            # Retrieve the user's last viewed subject from progress model
            user = self.request.user
            progress_queryset = Progress.objects.filter(user=user)

            last_subject = progress_queryset.last()

            # Check if a user has any saved progress
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
                context['grade'] = user.academicprofile.current_class.grade

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
