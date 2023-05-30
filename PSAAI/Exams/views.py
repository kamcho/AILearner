from django.shortcuts import render

# Create your views here
from django.views.generic import TemplateView


class Exams(TemplateView):
    template_name = 'Exams/exams.html'
