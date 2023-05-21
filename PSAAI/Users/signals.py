from django.db.models.signals import post_save
from .models import MyUser,PersonalProfile,AcademicProfile
from django.dispatch import receiver


@receiver(post_save,sender=MyUser)
def create_rofile(sender,instance,created,**kwargs):
    if created:
        PersonalProfile.objects.create(user=instance)
        AcademicProfile.objects.create(user=instance)
