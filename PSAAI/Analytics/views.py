from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.db.models import Count
from django.views.generic import TemplateView
from Exams.models import *
from Teacher.models import *
from Users.models import PersonalProfile


class IsStudent(UserPassesTestMixin):
    """
        ensure email passed is that of a student
    """
    def test_func(self):
        user_email = self.kwargs['mail']  # Get the user's email from the URL
        try:
            user = self.request.user.uuid
            # Get a user with the passed email
            student = PersonalProfile.objects.get(user__email=user_email)

            return student.ref_id == user  # limits viewership to students in watch list only
        except (DatabaseError, ObjectDoesNotExist, Exception):
            # Any exceptions occurrence limits view
            return False


class OverallAnalytics(LoginRequiredMixin, IsStudent, TemplateView):
    """
        view students tests analysis
    """
    template_name = 'Analytics/overall_analytics.html'

    def get_context_data(self, **kwargs):
        context = super(OverallAnalytics, self).get_context_data(**kwargs)
        user_email = self.kwargs['mail']  # Get the user's email from the URL

        try:
            # Try to retrieve the user by their email
            user = MyUser.objects.get(email=user_email)

            # Fetch analytics data for the user's tests
            tests = StudentTest.objects.filter(user=user).values('subject__id') \
                .annotate(subject_count=Count('subject__name')).order_by('subject__name').distinct()

            context['tests'] = tests
            context['child'] = user
        except MyUser.DoesNotExist:
            # Handle the case when the user does not exist
            messages.error(self.request, f'A user with email "{user_email}" does not exist')
        except Exception:
            # Handle other unexpected errors
            messages.error(self.request, 'An error occurred. We are fixing it.')

        return context


class SubjectAnalytics(LoginRequiredMixin, IsStudent, TemplateView):
    """
        View students performance on a given subject
    """
    template_name = 'Analytics/subject_analytics.html'

    def get_context_data(self, **kwargs):
        context = super(SubjectAnalytics, self).get_context_data(**kwargs)
        user = self.kwargs['mail']
        subject = self.kwargs['subject']

        try:
            user = MyUser.objects.get(email=user)  # get student's instance
            subject = Subject.objects.get(id=subject)  # get subject
            subject = subject.id  # get subject id
            student_tests = StudentTest.objects.filter(user=user, subject__id=subject)  # get topical tests
            class_test = ClassTestStudentTest.objects.filter(user=user, test__subject__id=subject)  # get class tests
            context['total_tests'] = int(student_tests.count()) + int(class_test.count())

            weakness = StudentsAnswers.objects.filter(user=user, quiz__subject__id=subject, is_correct=False). \
                values('quiz__topic__name').annotate(
                Count('quiz__topic__name')).order_by('quiz__topic__name')

            strength = StudentsAnswers.objects.filter(user=user, quiz__subject__id=subject, is_correct=True). \
                values('quiz__topic__name').annotate(
                Count('quiz__topic__name')).order_by('quiz__topic__name')

            context['subject'] = subject
            context['strength'] = strength
            context['weakness'] = weakness
            context['child'] = user

        # Handle any errors
        except MyUser.DoesNotExist:
            # Handle user does not exist
            messages.error(self.request, f'a user with email - {user} does not exist')
        except Subject.DoesNotExist:
            # Handle subject does not exist
            messages.error(self.request, 'Subject not found !!! did you edit the url if not contact us.')
        except Subject.MultipleObjectsReturned:
            # Handle multiple subjects returned
            messages.error(self.request, 'An error occurred were fixing it')

        except Exception:
            # Handle any other exceptions

            messages.error(self.request, 'An error occurred were fixing it')

        return context
