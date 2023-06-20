from django.urls import path
from .views import *


urlpatterns = [

    path('Subscription/', Subscribe.as_view(), name='subscription'),
    path('Card-Payment/', StripeCard.as_view(), name='stripe-pay')
    ]