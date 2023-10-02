from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


def index(request):
    return render(request, "Support/index.html")


def room(request, room_name):
    return render(request, "Support/room.html", {"room_name": room_name})
