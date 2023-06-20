from django.shortcuts import render
from django.views.generic import TemplateView
from .models import MySubscription,Subscriptions
# Create your views here.


class Subscribe(TemplateView):
    template_name = 'Subscription/subscription.html'

    def get_context_data(self, **kwargs):
        context = super(Subscribe, self).get_context_data(**kwargs)
        user = self.request.user
        context['subscriptions'] = Subscriptions.objects.all()
        context['my_subscription'] = MySubscription.objects.filter(user=user)

        return context


class StripeCard(TemplateView):
    template_name = 'Subscription/card.html'


