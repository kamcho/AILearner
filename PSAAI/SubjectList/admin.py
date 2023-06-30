from django.contrib import admin
from .models import *
# Register your models here.

# admin.site.register(MySubjects)
admin.site.register(Subject)
admin.site.register(Course)
admin.site.register(MySubjects)
admin.site.register(Topic)
admin.site.register(Subtopic)
admin.site.register(Progress)
admin.site.register(Notifications)
admin.site.register(OnlineClass)
admin.site.register(VideoChannel)