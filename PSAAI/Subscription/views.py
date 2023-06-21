from django.shortcuts import render
from django.views.generic import TemplateView

from Users.models import MyUser
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

    def post(self, request, *args, **kwargs):
        # Get the user's card information from the form
        if request.method=="POST":
            card_number = request.POST.get("card")
            exp_month = request.POST.get("month")
            exp_year = request.POST.get("year")
            cvc = request.POST.get("cvc")
            names=request.POST.get('names')
            currency=request.POST.get('currency')
            amount=request.POST.get('amount')


            print(card_number,currency,amount)
            token=stripe.Token.create(
                  card={
                    'number': card_number,
                    'exp_month': exp_month,
                    'exp_year': exp_year,
                    'cvc': cvc,
                      "name":names,

                  },

                )
            customer = stripe.Customer.create(
                source=token, email=request.user, name=names
            )
            # print(customer)

            # # Create a Stripe Charge object to process the payment
            amount=int(amount)*100
            currency=currency.lower()
            charge = stripe.Charge.create(
                amount=amount,
                currency=currency,
                customer=customer.id,
                description="Test payment",
                metadata={
                    'project_id': request.session['project-id'],
                    'user': request.user
                }
            )

            # # Render a confirmation page if the payment was successful
            return self.render_to_response({"success": True})

@csrf_exempt
def StripeWebhookView(request):
    # @csrf_protect

    if request.method=="POST":
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        endpoint_secret = "whsec_WLix6iladiKi5cALUPKuaPolsf8JKH1H"

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
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
            amount=charge['amount']
            project_id=charge['metadata']['project_id']
            transact_id=charge['id']
            brand=charge['payment_method_details']['card']['brand']
            currency=charge['currency']
            country=charge['payment_method_details']['card']['country']
            name=charge['billing_details']['name']
            created=charge['created']
            user=charge['metadata']['user']
            print(type(amount))
            print("\n\n\n\n\n\n\n")
            user=MyUser.objects.get(email=user)
            payment = StripeCardPayments.objects.create(
                user=user,
                amount=amount,

                transact_id=transact_id,

                currency=currency,
                name=name,
                country=country,
                brand=brand,
                created=created
            )
            payment.save()


            secret_key='sk_test_51MrhGPHSDxMMHnYTxwz5LLK9vGRHde981TLoCjmE9HNOmtbvAlIZbn9eCk29JFq98zziGrwKOxfj1ol5N9TDEOHo00eHUdjtjw'
            # ... handle other event types
        else:
            print('Unhandled event type {}'.format(event['type']))
        return HttpResponse(status=200)
