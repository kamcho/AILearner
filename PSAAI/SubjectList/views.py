from django.http import HttpResponse
from django.shortcuts import render, redirect
from itsdangerous import json

from .models import *
# Create your views here.
from django.views.generic import TemplateView


class Academia(TemplateView):
    template_name = 'SubjectList/academia.html'

    def get_context_data(self,*args,**kwargs):
        context=super(Academia, self).get_context_data(**kwargs)
        context['sciences'] = Course.objects.filter(discipline='science')
        context['literature'] = Course.objects.filter(discipline='literature')
        context['social'] = Course.objects.filter(discipline='social')

        return context

    def post(self,request):
        if request.method == "POST":
            user = MyUser.objects.get(email=request.user)
            print(user)
            subjects = request.POST.getlist('subjects')

            # Perform operations with the selected subjects
            for subject in subjects:
                # Do something with each selected subject ID
                print(subject)
            entry = MySubjects.objects.get(user=user)

            entry.name.set(subjects)
            # logged = MyUser.objects.get(email=request.user)
            #
            # friend = MyUser.objects.get(pk=self.kwargs['pk'])
            #
            # my_list = FriendList.objects.get(user=logged)
            #
            # my_list.friends.add(friend)


            return HttpResponse(subjects)



