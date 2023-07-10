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
admin.site.register(TopicExamNotifications)
admin.site.register(TopicalExamResults)
admin.site.register(PaymentNotifications)
admin.site.register(SubscriptionNotifications)
admin.site.register(ClassBookingNotifications)
admin.site.register(ClassBooking)
admin.site.register(OnlineClass)
admin.site.register(VideoChannel)
admin.site.register(AccountInquiries)
admin.site.register(AcademicInquiries)