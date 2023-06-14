from django.shortcuts import render, redirect
from SubjectList.models import Course, MySubjects
from .models import *
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

        question_index = self.request.session.get('index1', 0)
        questions = TopicalQuiz.objects.filter(topic__name=kwargs['pk'])
        if question_index >= len(questions):
            # The exam is completed, redirect to a summary page
            return redirect('home')
        else:
            current_question = questions[question_index]
            context['quiz'] =  current_question
            context['list']=questions
            return context

    def post(self, request, *args, **kwargs):
        question_index = request.session.get('index1', 0)
        questions = TopicalQuiz.objects.filter(topic__name=kwargs['pk'])
        print(question_index,len(questions))
        if question_index >= len(questions)-1:
            # The exam is completed, redirect to a summary page
            if 'index1' in request.session:
                del request.session['index1']
            return redirect('home')
        else:
            current_question = questions[question_index]
            # answer_text = request.POST.get('answer')
            # answer = Answer(question=current_question, student=request.user, answer_text=answer_text)
            # answer.save()
            request.session['index1'] = question_index + 1
            return redirect(request.path)
