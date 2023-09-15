import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, TemplateView
from SubjectList.models import Progress, Topic, Subject
from Users.forms import UserRegisterForm
from Users.models import PersonalProfile, MyUser, AcademicProfile
import logging

logger = logging.getLogger('django')



class RegisterView(CreateView):
    template_name = "Users/register.html"
    form_class = UserRegisterForm

    def get_success_url(self):
        return reverse('login')




class Login(TemplateView):
    template_name = 'Users/login.html'

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            # Create an instance of the AuthenticationForm and populate it with user-submitted data

            username = self.request.POST.get('email')
            password = self.request.POST.get('password')
            user = authenticate(self.request, username=username, password=password)

            if user is not None:
                # Log the user in
                login(self.request, user)
                # Redirect to a success page
                return redirect('redirect')
            else:
                # Return an error message if authentication fails
                messages.error(self.request, "Invalid username or password. Try again !")
                return redirect(self.request.get_full_path())


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

                context['base_html'] = 'Users/base.html'
                academic_profile = AcademicProfile.objects.get(user=self.request.user)
                grade = academic_profile.current_class.grade

                subjects = Subject.objects.filter(grade=grade)
                if not subjects:
                    raise Subject.DoesNotExist
                context['subjects'] = subjects
            elif self.request.user.role == 'Guardian':
                context['base_html'] = 'Guardian/baseg.html'
            elif self.request.user.role == 'Teacher':
                context['base_html'] = 'Teacher/teachers_base.html'
            elif self.request.user.role == 'Supervisor':
                context['base_html'] = 'Supervisor/base.html'
            else:
                # If logged in user's role doesn't match any criteria log out the user and show message
                messages.error(self.request, 'You are not authorised to use this system!')
                # redirect('logout')


        except Subject.DoesNotExist as e:
            messages.error(self.request, 'An error occurred when trying to get'
                                         ' your course information. Don"t be alarmed we are fixing it.')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            # Save Log to database
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
                    'model': 'Subject',
                }
            )

        except AttributeError as e:
            messages.error(self.request, 'You did not specify the current class'
                                         ' you are in. Please contact @support immediately')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            # Save Log to database
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

                    'model': 'AcademicProfile',
                    # Add more custom fields as needed
                }
            )

        except ObjectDoesNotExist as e:
            messages.error(self.request, 'An error occurred when trying to get'
                                         ' your course information. Don"t be alarmed we have fixed it.')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            logger.warning(
                error_message,
                exc_info=True,  # Include exception info in the log message
                extra={
                    'app_name': __name__,
                    'url': self.request.get_full_path(),
                    'school': uuid.uuid4(),
                    'error_type': error_type,
                    'user': self.request.user,
                    'level': 'Warning',
                    'model': 'AcademicProfile',
                }
            )
            academic_profile = AcademicProfile.objects.create(user=self.request.user)
        except Exception as e:
            messages.error(self.request, 'An error occurred. Please contact @support')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            # Save Log to database
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
                    # Add more custom fields as needed
                }
            )

        return context

    def post(self, args, **kwargs):
        # Check for Post requests
        if self.request.method == "POST":
            user = self.request.user
            # Check which button is clicked
            if 'profile' in self.request.POST:
                try:


                        # Get logged in user's profile for editing
                        profile = PersonalProfile.objects.get(user=user)  # get users personal profile
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


                except PersonalProfile.DoesNotExist as e:
                    # Create personal profile if none is found
                    messages.error(self.request, 'OOOps that did not work, Please try again!!')
                    personal_profile = PersonalProfile.objects.create(user=user)
                    error_message = str(e)  # Get the error message as a string
                    error_type = type(e).__name__

                    # Save Log to database
                    logger.critical(
                        error_message,
                        exc_info=True,  # Include exception info in the log message
                        extra={
                            'app_name': __name__,
                            'url': self.request.get_full_path(),
                            'school': uuid.uuid4(),
                            'error_type': error_type,
                            'user': self.request.user,
                            'level': 'Warning',
                            'model': 'PersonalProfile',
                        }
                    )


                except Exception as e:
                    # Handle any unhandled errors
                    messages.error(self.request, 'Sorry, there was an issue updating your profile. Please try again.')
                    error_message = str(e)  # Get the error message as a string
                    error_type = type(e).__name__

                    logger.critical(
                        error_message,
                        exc_info=True,  # Include exception info in the log message
                        extra={
                            'app_name': __name__,
                            'url': self.request.get_full_path(),
                            'school': uuid.uuid4(),
                            'error_type': 'DatabaseError',
                            'user': self.request.user,
                            'level': 'Critical',
                            'model': 'Database Error',
                        }
                    )

                # Add a learner to a guardians watch list
            elif 'attachment' in self.request.POST:
                try:
                    if user.role == 'Guardian':
                        mail = self.request.POST.get('mail')
                        name = self.request.POST.get('name')

                        learner = PersonalProfile.objects.filter(user__email=mail).first()  # get users profile
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

                    else:
                        messages.error(self.request, 'Sorry, You are not authorised to perform this action.')
                except Exception as e:
                    # Handle any exceptions
                    messages.error(self.request, 'Sorry, An error occurred. Please try again later !!')
                    error_message = str(e)  # Get the error message as a string
                    error_type = type(e).__name__

                    logger.critical(
                        error_message,
                        exc_info=True,  # Include exception info in the log message
                        extra={
                            'app_name': __name__,
                            'url': self.request.get_full_path(),
                            'school': uuid.uuid4(),
                            'error_type': 'DatabaseError',
                            'user': self.request.user,
                            'level': 'Critical',
                            'model': 'DatabaseError',
                        }
                    )

        return redirect(self.request.get_full_path())


class LoginRedirect(LoginRequiredMixin, TemplateView):
    """
        Redirect a user based on their role
    """
    template_name = 'Users/login_redirect.html'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        try:
            user = self.request.user
            role = user.role
            profile = self.request.user.personalprofile
            f_name = profile.f_name
        except ObjectDoesNotExist as e:
            profile = PersonalProfile.objects.create(user=user)
            f_name = profile.f_name
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
                    'level': 'Warning',
                    'model': 'PersonalProfile',
                }
            )
        except Exception as e:
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
                    'level': 'Warning',
                    'model': 'DatabaseError',
                }
            )
        finally:

            # If a user has not updated their profile redirect them to profile editing page
            if f_name == '':
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

                    logger.critical(
                        'Unauthorised Login',
                        exc_info=True,  # Include exception info in the log message
                        extra={
                            'app_name': __name__,
                            'url': self.request.get_full_path(),
                            'school': uuid.uuid4(),
                            'error_type': 'ForbiddenLogin',
                            'user': self.request.user,
                            'level': 'Critical',
                            'model': 'myUser',
                        }
                    )
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


            # if no profile matching query is found, create it and update it
            except PersonalProfile.ObjectDoesNotExist as e:
                PersonalProfile.objects.create(user=user)
                finish_profile_setup(user=user, f_name=f_name, l_name=l_name, surname=surname, phone=phone)
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.warning(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': uuid.uuid4(),
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Warning',
                        'model': 'PersonalProfile',
                    }
                )


            except Exception as e:
                messages.error(request, 'We could not process your request, try again.!!')
                error_message = str(e)  # Get the error message as a string
                error_type = type(e).__name__

                logger.warning(
                    error_message,
                    exc_info=True,  # Include exception info in the log message
                    extra={
                        'app_name': __name__,
                        'url': self.request.get_full_path(),
                        'school': uuid.uuid4(),
                        'error_type': error_type,
                        'user': self.request.user,
                        'level': 'Warning',
                        'model': 'DatabaseError',
                    }
                )
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
            academic_profile = AcademicProfile.objects.get(user=user)

            print(academic_profile)
            grade = academic_profile.current_class.grade
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
                context['grade'] = grade



        except AttributeError as e:
            context['grade'] = 4
            messages.error(self.request, 'You did not specify the current class'
                                         ' you are in. Please contact @support immediately')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            # Save Log to database
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

                    'model': 'AcademicProfile',
                    # Add more custom fields as needed
                }
            )

        except Exception as e:
            messages.error(self.request, 'An error occurred. Please contact @support')
            error_message = str(e)  # Get the error message as a string
            error_type = type(e).__name__

            # Save Log to database
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
                    # Add more custom fields as needed
                }
            )

        except AcademicProfile.DoesNotExist as e:
            academic_profile = AcademicProfile.objects.create(user=user)
            context['grade'] = 4
            messages.error(self.request, 'Dear user, you have not specified the current class you are in. Please contact @support')

            # Handle database errors gracefully
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
                    'model': 'AcademicProfile',
                }
            )


        return context

    def test_func(self):
        """
        Check if the user has the required role for accessing this view.
        """
        role = self.request.user.role

        return role == 'Student'
