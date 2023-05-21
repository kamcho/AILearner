from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from django.views.generic import CreateView, DetailView, TemplateView

from Users.forms import UserRegisterForm
from Users.models import PersonalProfile


class RegisterView(CreateView):
    template_name = "Users/register.html"

    form_class = UserRegisterForm
    # success_message = "YOUR ACCOUNT HAS BEEN CREATED SUCCESSFULLY"
    def get_success_url(self):
        return reverse('login')


class MyProfile(DetailView):
    model = PersonalProfile
    template_name = "Users/profile.html"

class Home(TemplateView):
    template_name = 'Users/home.html'
