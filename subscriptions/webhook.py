from django.utils import timezone
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription, SubscriptionPlan, BookPurchase
from books.models import Books
from django.contrib.auth.models import User
from datetime import timedelta

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    print('Stripe Signature Header:', sig_header)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        print('All is ok')
    except ValueError as e:
        print('ValueError:', str(e))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print('SignatureVerificationError:', str(e))
        return HttpResponse(status=400)

    print('Received event:', event['type'])
    print('Timestamp:', event['data']['object']['created'])

    current_time = timezone.now().timestamp()
    event_time = event['data']['object']['created']
    if current_time - event_time > 300:  # Слишком старая временная метка
        print('Слишком старая временная метка события')
        return HttpResponse(status=400)

    # Обработка событий
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    return HttpResponse(status=200)


def handle_checkout_session(session):
    print(session)
    customer_email = session.get('customer_email')
    payment_status = session.get('payment_status')
    metadata = session.get('metadata', {})
    purchase_type = metadata.get('purchase_type')

    print(f'Processing session for {customer_email}, payment status: {payment_status}, purchase type: {purchase_type}')

    if payment_status == 'paid':
        if purchase_type == 'subscription':
            # Обработка подписки
            plan_name = metadata.get('plan_name')  # Достаем название плана из метаданных
            print(f"Plan name from metadata: {plan_name}")
            try:
                plan = SubscriptionPlan.objects.get(name=plan_name)
                user = User.objects.get(email=customer_email)
                print(f'User: {user}, Plan: {plan}')

                if str(plan) == 'M':
                    Subscription.objects.update_or_create(
                        user=user,
                        defaults={
                            'plan': plan,
                            'start_date': timezone.now(),
                            'end_date': timezone.now() + timedelta(days=30),
                        }
                    )
                    print(f'Подписка для {customer_email} на план {plan_name} успешно создана.')
                elif str(plan) == 'Y':
                    Subscription.objects.update_or_create(
                        user=user,
                        defaults={
                            'plan': plan,
                            'start_date': timezone.now(),
                            'end_date': timezone.now() + timedelta(days=365),
                        }
                    )
                    print(f'Подписка для {customer_email} на план {plan_name} успешно создана.')
            except SubscriptionPlan.DoesNotExist:
                print(f'План подписки с именем {plan_name} не найден.')
            except User.DoesNotExist:
                print(f'Пользователь с email {customer_email} не найден.')

            except Exception as e:
                print(f'Ошибка при обработке подписки: {str(e)}')

        elif purchase_type == 'book':
            # Обработка покупки книги
            book_id = metadata.get('item_id')  # Достаем ID книги из метаданных
            try:
                book = Books.objects.get(id=book_id)
                user = User.objects.get(email=customer_email)
                BookPurchase.objects.create(user=user, book=book)
                print(f'Книга {book.title} успешно куплена пользователем {customer_email}.')
            except Books.DoesNotExist:
                print(f'Книга с ID {book_id} не найдена.')
            except User.DoesNotExist:
                print(f'Пользователь с email {customer_email} не найден.')
            except Exception as e:
                print(f'Ошибка при обработке покупки книги: {str(e)}')
