import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import Subscription, SubscriptionPlan, BookPurchase
from books.models import Books
from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return HttpResponse(status=200)


def handle_checkout_session(session):
    customer_email = session.get('customer_email')
    payment_status = session.get('payment_status')

    if payment_status == 'paid':
        metadata = session.get('metadata', {})
        purchase_type = metadata.get('purchase_type')
        item_id = metadata.get('item_id')

        if purchase_type == 'subscription':
            plan_name = session['display_items'][0]['custom']['name']
            plan = SubscriptionPlan.objects.get(name=plan_name)
            user = User.objects.get(email=customer_email)
            subscription, created = Subscription.objects.get_or_create(user=user, defaults={'plan': plan})
            if not created:
                subscription.plan = plan
                subscription.start_date = now()
                subscription.end_date = None
                subscription.save()

        elif purchase_type == 'book':

            book = Books.objects.get(id=item_id)
            user = User.objects.get(email=customer_email)
            BookPurchase.objects.create(user=user, book=book)
