from django.shortcuts import render
from SubjectList.models import Course, MySubjects
from .models import KCSEExam,KCSEQuiz,KCSEAnswers
# Create your views here
from django.views.generic import TemplateView


class Exams(TemplateView):
    template_name = 'Exams/exams.html'

    def get_context_data(self, **kwargs):
        context = super(Exams, self).get_context_data(**kwargs)
        context['subjects'] = MySubjects.objects.filter(user=self.request.user)

        return context

class ExamCourseList(TemplateView):
    template_name = 'Exams/year_select.html'

    def get_context_data(self, **kwargs):
        context = super(ExamCourseList, self).get_context_data(**kwargs)
        context['exams'] = KCSEExam.objects.filter(subject = self.kwargs['name'])

        return context
