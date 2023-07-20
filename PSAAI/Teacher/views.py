from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from Exams.models import TopicalQuizes, TopicalQuizAnswers
from SubjectList.models import Topic, Subtopic
from .models import *
# Create your views here.
from django.views.generic import TemplateView
from django.db import IntegrityError


class TeacherView(TemplateView):
    template_name = 'Teacher/teachers_home.html'


class StudentsView(TemplateView):
    template_name = 'Teacher/students_list.html'

    def get_context_data(self, **kwargs):
        context = super(StudentsView, self).get_context_data(**kwargs)

        return context


class ClassesView(TemplateView):
    template_name = 'Teacher/my_classes.html'

    def get_context_data(self, **kwargs):
        context = super(ClassesView, self).get_context_data(**kwargs)
        my_class = MyClasses.objects.filter(user=self.request.user)
        context['my_classes'] = my_class

        return context


class InitialiseCreateTest(TemplateView):
    template_name = 'Teacher/initialise_create_test.html'

    def get_context_data(self, **kwargs):
        context = super(InitialiseCreateTest, self).get_context_data(**kwargs)

        context['classes'] = StudentList.objects.filter(user=self.request.user)
        return context

    def post(self, request, **kwargs):
        if self.request.method == "POST":
            subject = self.request.POST.get('subject')
            class_id = self.request.POST.get('class-id')
            exam_type = self.request.POST.get('exam-type')
            selection_type = self.request.POST.get('selection-type')
            size = self.request.POST.get('test-size')
            date = self.request.POST.get('date')

            if subject and exam_type and selection_type and size and date and class_id:
                test_data = {'subject': subject, 'exam_type': exam_type, 'date': date,
                             'selection_type': selection_type, 'size': size, 'class_id': class_id}
                self.request.session['test_data'] = test_data

                if selection_type == 'user':
                    return redirect('user-question-selection', subject)

                elif selection_type == 'system':
                    return redirect('system-question-selection')

                else:
                    return redirect(self.request.get_full_path())
            else:
                return redirect(self.request.get_full_path())


def load_class(request):
    subject = request.GET.get('subject')
    classes = StudentList.objects.filter(user=request.user, subject=subject)
    class_data = [{'id': class_obj.class_id.id, 'name': class_obj.class_id.class_name} for class_obj in classes]
    print(class_data)
    return JsonResponse(class_data, safe=False)


def get_topical_quizzes(request):
    topic_id = request.GET.get('topic_id')
    questions = TopicalQuizes.objects.filter(topic_id=topic_id)

    # Prepare the data in a format suitable for JSON serialization
    questions_data = [{'id': question.id, 'quiz': question.quiz} for question in questions]

    return JsonResponse({'questions': questions_data})


def add_question_to_session(request):
    question_id = request.POST.get('question_id')
    question_ids = request.session.get('selected', [])
    # del request.session['selected']
    if question_id not in question_ids:
        question_ids.append(question_id)
        request.session['selected'] = question_ids

    return JsonResponse({'success': True, 'session_data': len(question_ids)})


class UserQuestionsSelect(TemplateView):
    template_name = 'Teacher/user_questions_select.html'

    def get_context_data(self, **kwargs):
        context = super(UserQuestionsSelect, self).get_context_data(**kwargs)
        subject = self.kwargs['subject']
        context['topics'] = Topic.objects.filter(subject=subject)

        return context


def SystemQuestionsSelect(request):
    subject = request.session['test_data']['subject']

    quizes = TopicalQuizes.objects.filter(subject=subject).order_by('?')[:15]
    print(quizes)
    items = []
    try:
        del request.session['selected']

    except KeyError:
        pass
    finally:

        for item in list(quizes.values_list('id', flat=True)):
            items.append(str(item))
        request.session['selected'] = items

        return redirect('save-test')


class SaveTest(TemplateView):
    template_name = 'Teacher/save_test.html'

    def get_context_data(self, **kwargs):
        context = super(SaveTest, self).get_context_data(**kwargs)
        ids = self.request.session.get('selected', [])
        class_id = self.request.session['test_data']['class_id']
        quizes = TopicalQuizes.objects.filter(id__in=ids)
        context['quizzes'] = quizes
        class_name = SchoolClass.objects.filter(id=class_id).first()
        context['class'] = class_name
        print(ids, quizes)

        return context

    def post(self, request, **kwargs):
        if self.request.method == "POST":
            teacher = self.request.user
            subject = self.request.session['test_data']['subject']
            size = self.request.session['test_data']['size']
            date = self.request.session['test_data']['date']
            subject = Subject.objects.filter(id=subject).first()
            ids = self.request.session.get('selected', [])

            print(date)
            try:
                test = ClassTest(teacher=teacher, subject=subject, test_size=size, expiry=date)
                test.save()
                test.quiz.set(ids)

                message = f'The monthly {subject.name} is now available. Please finish before {date}.'
                about = f'{subject.name} class-test is now available.'
                notification_type = 'class-test'
                class_instance = ClassTest.objects.filter(uuid=test.uuid).first()
                msg = ClassTestNotifications.objects.create(user=teacher, subject=subject,
                                                            class_id=class_instance.class_id, test=class_instance, message=message,
                                                            notification_type=notification_type, about=about)
                del self.request.session['test_data']
                del self.request.session['selected']

                return redirect('teachers-home')


            except IntegrityError:

                return redirect(self.request.get_full_path())


class TaskSelection(TemplateView):
    template_name = 'Guardian/task_select.html'

    def get_context_data(self, **kwargs):
        context = super(TaskSelection, self).get_context_data(**kwargs)

        context['email'] = self.kwargs['email']

        return context


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
