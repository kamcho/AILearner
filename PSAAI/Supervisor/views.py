import datetime

from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import TemplateView

from Exams.models import TopicalQuizes, KNECGradeExams, TopicalQuizAnswers
from SubjectList.models import Subject, Topic, Subtopic
from Supervisor.models import KnecQuizzes, KnecQuizAnswers, Schools


class SupervisorHomeView(TemplateView):
    template_name = 'Supervisor/supervisor_home.html'

    def get_context_data(self, **kwargs):
        context = super(SupervisorHomeView, self).get_context_data(**kwargs)
        return context


class TestTaskView(TemplateView):
    template_name = 'Supervisor/test_type_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class KNECExamConfig(TemplateView):
    template_name = 'Supervisor/knec_config.html'

    def get_context_data(self, **kwargs):
        context = super(KNECExamConfig, self).get_context_data(**kwargs)
        subjects = Subject.objects.all()
        tests = KNECGradeExams.objects.all()
        context['session_data'] = self.request.session.get('knec_config', None)
        context['tests'] = tests
        context['subjects'] = subjects
        return context

    def post(self, request):
        if request.method == "POST":
            date = datetime.datetime.now().strftime('%Y')
            user = request.user
            p_subject = request.POST.get('subject')
            grade = request.POST.get('grade')
            term = request.POST.get('term')
            subject = Subject.objects.get(id=p_subject)
            test = KNECGradeExams.objects.filter(grade=grade, subject=subject, term=term, year=date).first()
            if test:
                test_id = test.uuid
            else:

                knec_test = KNECGradeExams.objects.create(teacher=user, grade=grade, subject=subject, term=term,
                                                          test_size='50', year=date)
                test_id = knec_test.uuid
            knec_config = {'subject': p_subject, 'grade': grade, 'term': term, 'year': date}
            request.session['knec_config'] = knec_config

            return redirect('knec-add-quiz', subject, test_id)


class KNECAddQuiz(TemplateView):
    template_name = 'Supervisor/knec_add_quiz.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test_id = self.kwargs['uuid']
        context['subject'] = self.request.session.get('knec_config')['subject']
        context['term'] = self.request.session.get('knec_config')['term']
        context['test_id'] = test_id
        test = KNECGradeExams.objects.get(uuid=test_id)
        context['count'] = test.quiz.all().count()

        return context

    def post(self, request, *args, **kwargs):
        if request.method == "POST":  # Corrected method name to uppercase
            url_subject = self.kwargs['subject']
            test_id = self.kwargs['uuid']
            quiz = request.POST.get('quiz')
            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            sub_topic = request.POST.get('subtopic')
            if quiz and sub_topic and subject and topic:
                data = {'quiz': quiz, 'subject': subject, 'topic': topic, 'subtopic': sub_topic}
                request.session['quiz'] = data
                return redirect('knec-add-selection', subject, test_id)
            else:
                return redirect('knec-add-quiz', url_subject, test_id)


class KNECAddSelection(TemplateView):
    template_name = 'Supervisor/knec_add_selection.html'

    def get_context_data(self, **kwargs):
        context = super(KNECAddSelection, self).get_context_data(**kwargs)
        context['quiz'] = self.request.session.get('quiz')

        return context

    def post(self, request, *args, **kwargs):
        if self.request.method == 'POST':
            subject = self.kwargs['subject']
            test_id = self.kwargs['uuid']

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
                return redirect('save-knec-quiz', subject, test_id)

            else:
                return redirect('knec-add-selection', subject, test_id)


def parse_quiz(request, *args, **kwargs):
    session_quiz_data = request.session.get('quiz')

    topic = session_quiz_data['topic']
    sub_topic = session_quiz_data['subtopic']
    quizz = session_quiz_data['quiz']
    session_selection_data = request.session.get('selection_info')
    selection1 = session_selection_data['selection1']
    selection2 = session_selection_data['selection2']
    selection3 = session_selection_data['selection3']
    selection4 = session_selection_data['selection4']

    return sub_topic, topic, quizz, selection1, selection2, selection3, selection4


def save_selection(test_quiz, selection1, selection2, selection3, selection4):
    quiz_answers = [
        KnecQuizAnswers(quiz=test_quiz, choice=selection1, is_correct=True),
        KnecQuizAnswers(quiz=test_quiz, choice=selection2, is_correct=False),
        KnecQuizAnswers(quiz=test_quiz, choice=selection3, is_correct=False),
        KnecQuizAnswers(quiz=test_quiz, choice=selection4, is_correct=False),
    ]
    with transaction.atomic():
        KnecQuizAnswers.objects.bulk_create(quiz_answers)
    return None


class SaveQuiz(TemplateView):
    template_name = 'Supervisor/save_quiz.html'

    def get_context_data(self, **kwargs):
        context = super(SaveQuiz, self).get_context_data(**kwargs)
        quiz = self.request.session.get('quiz')
        context['quiz'] = quiz
        context['selection'] = self.request.session.get('selection_info')
        context['subject'] = Subtopic.objects.filter(subject=quiz['subject']).first()

        return context

    def post(self, request, **kwargs):
        if request.method == 'POST':
            test_id = self.kwargs['uuid']
            subject = self.kwargs['subject']

            sub_topic, topic, quizz, selection1, selection2, selection3, selection4 = parse_quiz(request)
            db_sub_topic = Subtopic.objects.filter(id=sub_topic).first()
            test_quiz = KnecQuizzes.objects.create(subject=db_sub_topic.subject, topic=db_sub_topic.topic,
                                                   subtopic=db_sub_topic,
                                                   quiz=quizz)
            save_selection(test_quiz, selection1, selection2, selection3, selection4)

            knec_test = KNECGradeExams.objects.get(uuid=test_id)
            knec_test.quiz.add(test_quiz)

        else:
            print('no db')

        return redirect('knec-add-quiz', subject, test_id)


class TestReview(TemplateView):
    template_name = 'Supervisor/test_review.html'

    def get_context_data(self, **kwargs):
        context = super(TestReview, self).get_context_data(**kwargs)
        test_id = self.kwargs['uuid']
        test = KNECGradeExams.objects.get(uuid=test_id)
        quiz_uuids = [quiz.quiz for quiz in test.quiz.all()]
        print(quiz_uuids)

        context['quizzes'] = test.quiz.all()

        return context



class SchoolSelect(TemplateView):
    template_name = 'Supervisor/school_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schools = Schools.objects.all()
        context['schools'] = schools
        return context


class SchoolTaskSelect(TemplateView):
    template_name = 'Supervisor/school_task_select.html'

    def get_context_data(self, **kwargs):
        uuid = self.kwargs['uuid']
        context = super(SchoolTaskSelect, self).get_context_data(**kwargs)
        school = Schools.objects.get(uuid=uuid)
        context['school'] = school

        return context
