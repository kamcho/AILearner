from django.db.models import Count
from django.shortcuts import render
from django.views.generic import TemplateView

from Exams.models import *
# Create your views here.


class OverallAnalytics(TemplateView):
    template_name = 'Analytics/overall_analytics.html'

    def get_context_data(self, **kwargs):
        context = super(OverallAnalytics, self).get_context_data(**kwargs)
        user = self.request.user
        tests = StudentTest.objects.filter(user=user).values('subject__name', 'topic__name').annotate(Count('topic')).order_by('subject__name')
        context['tests'] = tests

        return context



