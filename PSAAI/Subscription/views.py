import datetime
import json
from datetime import timedelta
# views.py
import requests
from django.shortcuts import render, redirect

import base64
import hashlib
import datetime
import stripe
from django.db import DatabaseError, IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from requests.auth import HTTPBasicAuth
from stripe.error import StripeError

from SubjectList.models import PaymentNotifications
from Users.models import MyUser, PersonalProfile
from .models import MySubscription, Subscriptions, StripeCardPayments


# Create your views here.


class Subscribe(TemplateView):
    template_name = 'Subscription/subscription.html'

    def get_context_data(self, **kwargs):
        context = super(Subscribe, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            context['subscriptions'] = Subscriptions.objects.all()
            context['my_subscription'] = MySubscription.objects.filter(user=user)

            return context

        except DatabaseError:
            pass



def generate_access_token():
    consumer_key = '3r0PGbGzT0q4XX3aLnBHeyZrO9QlGnyx'
    consumer_secret = 'VbgYH9GK5GibFruV'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        return access_token
    else:
        return JsonResponse({'error': 'Token generation failed'}, status=response.status_code)


    return HttpResponse(status=405)


def generate_mpesa_password(paybill_number):

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    consumer_key = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    concatenated_string = f"{paybill_number}{consumer_key}{timestamp}"
    base64_encoded = base64.b64encode(concatenated_string.encode()).decode('utf-8')

    return base64_encoded


def initiate_payment(request):
    # Use your API credentials here
    consumer_key = 'uBAiPdLXOGEmOqjBYlh2Wt57ecTaRlyz'
    consumer_secret = 'rR5Ftd45gurgBaP2'
    paybill = "174379"
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    access_token = generate_access_token()
    password = generate_mpesa_password(paybill)

    payment_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    payload = {
        "BusinessShortCode": paybill,
        "Password": password,  # Generate password as per API documentation
        "Timestamp": timestamp,  # Use current timestamp
        "TransactionType": "CustomerPayBillOnline",
        "Amount": "1",
        "PartyA": "254711371265",
        "PartyB": paybill,
        "PhoneNumber": "254711371265",
        "CallBackURL": "https://81fb-105-163-157-153.ngrok-free.app/Subscription/callback/",
        "AccountReference": "E-Learning Subscription",
        "TransactionDesc": "pay 1ks to e-learner"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(payment_url, json=payload, headers=headers)
    return HttpResponse(response)



@csrf_exempt
def payment_callback(request):

    data = request.body.decode('utf-8')
    data = json.loads(data)
    print(data)

    return JsonResponse({'response':data})
