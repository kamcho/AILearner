from django.shortcuts import render
from SubjectList.models import Course, MySubjects
from .models import KCSEExam,KCSEQuiz,KCSEAnswers
# Create your views here
from django.views.generic import TemplateView, DetailView


class Exams(TemplateView):
    template_name = 'Exams/exams.html'

    def get_context_data(self, **kwargs):
        context = super(Exams, self).get_context_data(**kwargs)
        context['subjects'] = MySubjects.objects.filter(user=self.request.user)

        return context

class ExamList(TemplateView):
    template_name = 'Exams/year_select.html'

    def get_context_data(self, **kwargs):
        context = super(ExamList, self).get_context_data(**kwargs)
        context['exams'] = KCSEExam.objects.filter(subject = self.kwargs['name'])

        return context

class Tests(TemplateView):
    template_name = 'Exams/tests.html'


    def get_context_data(self, **kwargs):
        context = super(Tests, self).get_context_data(**kwargs)
        context['quizes'] = KCSEQuiz.objects.filter(unit=kwargs['pk']).order_by('number')

        return context
