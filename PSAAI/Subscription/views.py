import datetime
from datetime import timedelta

import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from SubjectList.models import PaymentNotifications
from Users.models import MyUser, PersonalProfile
from .models import MySubscription, Subscriptions, StripeCardPayments


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

    def get_context_data(self, **kwargs):
        context = super(StripeCard, self).get_context_data(**kwargs)
        subs = Subscriptions.objects.all()

        context['subs'] = subs
        kids = PersonalProfile.objects.filter(ref_id=self.request.user.uuid)
        context['kids'] = kids

        return context

    def post(self, request, *args, **kwargs):
        stripe.api_key = 'sk_test_51MrhGPHSDxMMHnYTxwz5LLK9vGRHde981TLoCjmE9HNOmtbvAlIZbn9eCk29JFq98zziGrwKOxfj1ol5N9TDEOHo00eHUdjtjw'
        if request.method == "POST":
            card_number = request.POST.get("card")
            exp_month = request.POST.get("month")
            exp_year = request.POST.get("year")
            cvc = request.POST.get("cvc")
            names = request.POST.get('names')
            selected = request.POST.getlist('selected_kids')
            type = request.POST.get('subscription')
            amount = request.POST.get('amount')
            token = stripe.Token.create(
                card={
                    'number': card_number,
                    'exp_month': exp_month,
                    'exp_year': exp_year,
                    'cvc': cvc,
                    "name": names,
                },
            )
            customer = stripe.Customer.create(
                source=token, email=request.user, name=names
            )
            amount = int(amount) * 100
            charge = stripe.Charge.create(
                amount=amount,
                currency='kes',
                customer=customer.id,
                description="Test payment",
                metadata={'students': ', '.join(selected),
                          'user': request.user,
                          'type': type,
                          },
            )
            return self.render_to_response({"success": True})


@csrf_exempt
def StripeWebhookView(request):
    # @csrf_protect

    if request.method == "POST":
        payload = request.body

        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        endpoint_secret = "whsec_WRS1nWAj4LEIt9vFZ0tMOM7bkynvjJlr"

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )


        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        except ValueError:
            print(payload)
            return HttpResponse(status=400)

        if event['type'] == 'charge.failed':
            charge = event['data']['object']
            print(charge)
        elif event['type'] == 'charge.pending':
            charge = event['data']['object']
            print(charge)
        elif event['type'] == 'charge.succeeded':
            charge = event['data']['object']
            print(charge['metadata'])
            amount = charge['amount']
            students = charge['metadata']['students']
            transact_id = charge['id']
            brand = charge['payment_method_details']['card']['brand']
            currency = charge['currency']
            country = charge['payment_method_details']['card']['country']
            name = charge['billing_details']['name']
            created = charge['created']
            user = charge['metadata']['user']
            sub = charge['metadata']['type']
            print(type(amount))
            print("\n\n\n\n\n\n\n")
            user = MyUser.objects.get(email=user)
            payment = StripeCardPayments.objects.create(
                user=user,
                amount=amount,

                transact_id=transact_id,
                student_list=students,
                type=sub,

                currency=currency,
                name=name,
                country=country,
                brand=brand,
                created=created
            )
            payment.save()
            update_subscription(students, sub)
            notify(user=user,amount=amount, beneficiaries=students, subscription_type=sub)

        else:
            print('Unhandled event type {}'.format(event['type']))
        return HttpResponse(status=200)


def update_subscription(users, type):
    email_list = [email.strip() for email in users.split(",")]
    print(type, '\n\n\n\n\n\n')

    for user in email_list:
        myuser = MyUser.objects.get(email=user)
        subscribe = MySubscription.objects.get(user=myuser)
        subs = Subscriptions.objects.get(type=type.title())
        print(myuser, subscribe)
        subscribe.type = subs
        subscribe.status = True
        expiry = subscribe.expiry + timedelta(days=30)
        subscribe.expiry = expiry
        subscribe.date = datetime.date.today()
        subscribe.save()

    return None


def notify(user, amount, beneficiaries, subscription_type):
    notification = PaymentNotifications.objects.create(user=user, beneficiaries=beneficiaries, amount=amount,
                                                       subscription_type=subscription_type)
    return None
