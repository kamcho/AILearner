from django.db import models

# Create your models here.
from Users.models import MyUser


class Subscriptions(models.Model):
    type = models.CharField(max_length=30,unique=True)
    amount = models.PositiveIntegerField()
    validity = models.CharField(max_length=10)

    def __str__(self):
        return str(self.type)

class MySubscription(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    type = models.ForeignKey(Subscriptions, to_field='type', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)
