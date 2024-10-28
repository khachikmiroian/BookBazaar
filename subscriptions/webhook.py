from django.utils import timezone
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription, SubscriptionPlan, BookPurchase
from books.models import Books
from datetime import timedelta
from .tasks import send_purchase_email
from accounts.models import MyUser
from django.db import transaction

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    current_time = timezone.now().timestamp()
    event_time = event['data']['object']['created']

    if current_time - event_time > 300:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return HttpResponse(status=200)


@transaction.atomic
def handle_checkout_session(session):
    customer_email = session.get('customer_email')
    payment_status = session.get('payment_status')
    metadata = session.get('metadata', {})
    purchase_type = metadata.get('purchase_type')

    if payment_status == 'paid':
        if purchase_type == 'subscription':
            plan_name = metadata.get('plan_name')

            try:
                plan = SubscriptionPlan.objects.get(name=plan_name)
                user = MyUser.objects.get(email=customer_email)
                current_subscription = Subscription.objects.filter(user=user, end_date__gt=timezone.now()).first()

                if str(plan) == 'M':
                    start_date = current_subscription.end_date if current_subscription else timezone.now()
                    end_date = start_date + timedelta(days=30)

                    Subscription.objects.update_or_create(
                        user=user,
                        defaults={
                            'plan': plan,
                            'start_date': timezone.now() if not current_subscription else current_subscription.start_date,
                            'end_date': end_date,
                        }
                    )
                    send_purchase_email.delay(user.email, 'subscription', plan_name, user.username)

                elif str(plan) == 'Y':
                    start_date = current_subscription.end_date if current_subscription else timezone.now()
                    end_date = start_date + timedelta(days=365)

                    Subscription.objects.update_or_create(
                        user=user,
                        defaults={
                            'plan': plan,
                            'start_date': timezone.now() if not current_subscription else current_subscription.start_date,
                            'end_date': end_date,
                        }
                    )
                    send_purchase_email.delay(user.email, 'subscription', plan_name, user.username)

            except SubscriptionPlan.DoesNotExist:
                pass
            except MyUser.DoesNotExist:
                pass
            except Exception:
                pass

        elif purchase_type == 'book':
            book_id = metadata.get('item_id')
            try:
                book = Books.objects.get(id=book_id)
                user = MyUser.objects.get(email=customer_email)

                BookPurchase.objects.create(user=user, book=book)

                send_purchase_email.delay(user.email, 'book', book.title, user.username)
            except Books.DoesNotExist:
                pass
            except MyUser.DoesNotExist:
                pass
            except Exception:
                pass
