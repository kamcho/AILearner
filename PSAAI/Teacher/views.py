from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from Exams.models import TopicalQuizes, TopicalQuizAnswers
from SubjectList.models import Topic, Subtopic
from .models import *
# Create your views here.
from django.views.generic import TemplateView


class TeacherView(TemplateView):
    template_name = 'Teacher/teachers_home.html'


class ClassView(TemplateView):
    template_name = 'Teacher/class.html'


def load_topic(request):
    subject_id = request.GET.get('subject_id')
    topics = Topic.objects.filter(subject=subject_id)
    topic_options = [{'id': topic.id, 'name': topic.name} for topic in topics]
    return JsonResponse(topic_options, safe=False)


def load_subtopics(request):
    topic_id = request.GET.get('topic_id')
    subtopics = Subtopic.objects.filter(topic_id=topic_id)
    subtopic_options = [{'id': subtopic.id, 'name': subtopic.name} for subtopic in subtopics]
    return JsonResponse(subtopic_options, safe=False)


class CreateQuestion(TemplateView):
    template_name = 'Teacher/create_question.html'

    def get_context_data(self, **kwargs):
        context = super(CreateQuestion, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            subjects = TeacherProfile.objects.get(user=user)
            context['subjects'] = subjects

            return context

        except TeacherProfile.MultipleObjectsReturned:
            pass
        except TeacherProfile.DoesNotExist:
            pass

    def post(self, request, **kwargs):
        if self.request.method == "POST":
            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            sub_topic = request.POST.get('subtopic')
            quiz = request.POST.get('quiz')

            if subject and topic and sub_topic:
                quiz_info = {'subject': subject, 'topic': topic, 'subtopic': sub_topic, 'quiz': quiz}
                request.session['quiz_info'] = quiz_info
                # quiz = TopicalQuizes.objects.create(subject=db_subject, topic=db_topic, subtopic=db_sub_topic, quiz=quiz)

                return redirect('add-answer')
            else:
                print('not values')


class AddAnswerSelection(TemplateView):
    template_name = 'Teacher/add_answer.html'

    def get_context_data(self, **kwargs):
        context = super(AddAnswerSelection, self).get_context_data(**kwargs)
        context['quiz'] = self.request.session.get('quiz_info')

        return context

    def post(self, request, **kwargs):
        if self.request.method == 'POST':
            selection1 = self.request.POST.get('selection1')
            selection2 = self.request.POST.get('selection2')
            selection3 = self.request.POST.get('selection3')
            selection4 = self.request.POST.get('selection4')
            if selection1 and selection2 and selection3 and selection4:
                self.request.session['selection_info'] = {'selection1': selection1,
                                                          'selection2': selection2,
                                                          'selection3': selection3,
                                                          'selection4': selection4
                                                          }
                return redirect('save-quiz')

            else:
                return redirect(self.request.get_full_path())


class SaveQuiz(TemplateView):
    template_name = 'Teacher/save_question.html'

    def get_context_data(self, **kwargs):
        context = super(SaveQuiz, self).get_context_data(**kwargs)
        subtopic = self.request.session.get('quiz_info')['subtopic']
        context['quiz'] = self.request.session.get('quiz_info')['quiz']
        context['subtopic'] = Subtopic.objects.filter(id=subtopic).first()
        context['selection'] = self.request.session.get('selection_info')

        return context

    def post(self, request, **kwargs):
        if request.method == 'POST':
            session_quiz_data = request.session.get('quiz_info')
            subject = session_quiz_data['subject']
            topic = session_quiz_data['topic']
            sub_topic = session_quiz_data['subtopic']
            quiz = session_quiz_data['quiz']
            session_selection_data = self.request.session.get('selection_info')
            selection1 = session_selection_data['selection1']
            selection2 = session_selection_data['selection2']
            selection3 = session_selection_data['selection3']
            selection4 = session_selection_data['selection4']
            db_subject = Subject.objects.filter(id=subject).first()
            db_topic = Topic.objects.filter(id=topic).first()
            db_sub_topic = Subtopic.objects.filter(id=sub_topic).first()
            print(db_subject, db_topic, db_sub_topic)
            if db_subject and db_sub_topic and db_topic:
                quiz = TopicalQuizes.objects.create(subject=db_subject, topic=db_topic, subtopic=db_sub_topic,
                                                    quiz=quiz)
                selection_1 = TopicalQuizAnswers.objects.create(quiz=quiz, choice=selection1, is_correct=True)
                selection_2 = TopicalQuizAnswers.objects.create(quiz=quiz, choice=selection2, is_correct=False)
                selection_3 = TopicalQuizAnswers.objects.create(quiz=quiz, choice=selection3, is_correct=False)
                selection_4 = TopicalQuizAnswers.objects.create(quiz=quiz, choice=selection4, is_correct=False)

        else:
            print('no db')

        return redirect('teachers-home')
