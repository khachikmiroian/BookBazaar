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

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        print("Webhook event constructed successfully.")
    except ValueError as e:
        print(f"ValueError: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f"SignatureVerificationError: {str(e)}")
        return HttpResponse(status=400)

    current_time = timezone.now().timestamp()
    event_time = event['data']['object']['created']
    print(f"Current time: {current_time}, Event time: {event_time}")

    if current_time - event_time > 300:
        print("Event is too old. Ignoring.")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        print("Processing checkout session completed event.")
        session = event['data']['object']
        handle_checkout_session(session)

    return HttpResponse(status=200)


def handle_checkout_session(session):
    print("Handling checkout session...")
    customer_email = session.get('customer_email')
    payment_status = session.get('payment_status')
    metadata = session.get('metadata', {})
    purchase_type = metadata.get('purchase_type')

    print(f'Customer Email: {customer_email}, Payment Status: {payment_status}, Purchase Type: {purchase_type}')

    if payment_status == 'paid':
        if purchase_type == 'subscription':
            plan_name = metadata.get('plan_name')

            try:
                print(f'Attempting to retrieve subscription plan: {plan_name}')
                plan = SubscriptionPlan.objects.get(name=plan_name)
                user = MyUser.objects.get(email=customer_email)

                # Получить текущую активную подписку пользователя, если есть
                current_subscription = Subscription.objects.filter(user=user, end_date__gt=timezone.now()).first()

                if str(plan) == 'M':
                    # Определить начальную дату: если есть активная подписка, используем её end_date
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
                    print(f'Subscription for {customer_email} on plan {plan_name} updated successfully.')

                elif str(plan) == 'Y':
                    # Аналогично для годовой подписки
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
                    print(f'Subscription for {customer_email} on plan {plan_name} updated successfully.')

            except SubscriptionPlan.DoesNotExist:
                print(f'Subscription plan with name {plan_name} not found.')
            except MyUser.DoesNotExist:
                print(f'User with email {customer_email} not found.')
            except Exception as e:
                print(f'Error processing subscription: {str(e)}')
        elif purchase_type == 'book':
            # Обработка покупки книги
            book_id = metadata.get('item_id')  # Достаем ID книги из метаданных
            try:
                print(f'Attempting to retrieve book with ID: {book_id}')
                book = Books.objects.get(id=book_id)
                user = MyUser.objects.get(email=customer_email)
                print(f'Found book: {book.title}, User: {user.email}')

                print('Creating book purchase...')
                BookPurchase.objects.create(user=user, book=book)

                send_purchase_email.delay(user.email, 'book', book.title, user.username)
                print(f'Book {book.title} successfully purchased by user {customer_email}.')
            except Books.DoesNotExist:
                print(f'Book with ID {book_id} not found.')
            except MyUser.DoesNotExist:
                print(f'User with email {customer_email} not found.')
            except Exception as e:
                print(f'Error processing book purchase: {str(e)}')
