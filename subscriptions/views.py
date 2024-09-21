from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views.generic import TemplateView, ListView
from django.conf import settings
from .models import SubscriptionPlan
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from subscriptions.models import BookPurchase
from books.models import Books
from accounts.models import Profile  # Замените 'your_app' на название приложения, где определен Profile
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


class SubscriptionsList(ListView):
    model = SubscriptionPlan
    template_name = 'subscription/subscription_list.html'
    context_object_name = 'subs'

    def get_queryset(self):
        return SubscriptionPlan.objects.all()


class SubscriptionView(TemplateView):
    template_name = 'subscription/subscription_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLISHABLE_KEY

        return context


@login_required
def create_subscription_session(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('subs:completed'))
        cancel_url = request.build_absolute_uri(reverse('subs:canceled'))

        # Данные сеанса оформления платежа Stripe
        session_data = {
            'payment_method_types': ['card'],
            'customer_email': request.user.email,
            'line_items': [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan.get_name_display(),
                    },
                    'unit_amount': int(plan.price * 100),
                },
                'quantity': 1,
            }],
            'mode': 'payment',
            'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': cancel_url,
        }

        # Создать сеанс оформления платежа Stripe
        session = stripe.checkout.Session.create(**session_data)

        # Перенаправить к платежной форме Stripe
        return redirect(session.url, code=303)
    else:
        return render(request, 'subscription/subscribe.html', {'plan': plan})


# @login_required
# def create_book_purchase_session(request, book_id):
#     book = get_object_or_404(Books, id=book_id)
#
#     if request.method == 'POST':
#         success_url = request.build_absolute_uri(reverse('subs:completed'))
#         cancel_url = request.build_absolute_uri(reverse('subs:canceled'))
#
#         # Данные сеанса оформления платежа Stripe
#         session_data = {
#             'payment_method_types': ['card'],
#             'customer_email': request.user.email,
#             'line_items': [{
#                 'price_data': {
#                     'currency': 'usd',
#                     'product_data': {
#                         'name': book.title,
#                     },
#                     'unit_amount': int(book.price * 100),
#                 },
#                 'quantity': 1,
#             }],
#             'mode': 'payment',
#             'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
#             'cancel_url': cancel_url,
#         }
#
#         # Создать сеанс оформления платежа Stripe
#         session = stripe.checkout.Session.create(**session_data)
#
#         # Перенаправить к платежной форме Stripe
#         return redirect(session.url, code=303)
#     else:
#         return render(request, 'books/book_detail.html', {'book': book.id})
#
#
# def payment_completed(request):
#     return render(request, 'subscription/completed.html')


def payment_canceled(request):
    return render(request, 'subscription/canceled.html')


stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid request method'}, status=400)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')  # Используем .get() вместо []
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    if sig_header is None:
        return JsonResponse({'status': 'missing signature header'}, status=400)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Неверные данные
        return JsonResponse({'status': 'invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Неверная подпись
        return JsonResponse({'status': 'invalid signature'}, status=400)

    # Обработка события успешного платежа
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session['customer_email']
        book_title = session['display_items'][0]['custom']['name']

        # Получить пользователя и книгу по информации из сессии
        user = User.objects.get(email=customer_email)
        book = Books.objects.get(title=book_title)

        # Создать запись о покупке книги
        BookPurchase.objects.create(user=user, book=book)

    return JsonResponse({'status': 'success'}, status=200)


@login_required
def create_book_purchase_session(request, book_id):
    book = get_object_or_404(Books, id=book_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('subs:completed'))
        cancel_url = request.build_absolute_uri(reverse('subs:canceled'))

        # Данные сеанса оформления платежа Stripe
        session_data = {
            'payment_method_types': ['card'],
            'customer_email': request.user.email,
            'line_items': [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': book.title,
                    },
                    'unit_amount': int(book.price * 100),
                },
                'quantity': 1,
            }],
            'mode': 'payment',
            'success_url': f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&book_id={book.id}",
            'cancel_url': cancel_url,
        }

        # Создать сеанс оформления платежа Stripe
        session = stripe.checkout.Session.create(**session_data)

        # Перенаправить к платежной форме Stripe
        return redirect(session.url, code=303)
    else:
        return render(request, 'books/book_detail.html', {'book': book.id})


@login_required
def payment_completed(request):
    # Получаем идентификатор сессии и идентификатор книги из URL параметров
    session_id = request.GET.get('session_id')
    book_id = request.GET.get('book_id')

    print('Получение параметров:', {'session_id': session_id, 'book_id': book_id})

    if session_id and book_id:
        try:
            # Проверяем сессию платежа через Stripe API
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid':
                # Если оплата прошла успешно, добавляем книгу в список купленных пользователем
                book = get_object_or_404(Books, id=book_id)
                profile = Profile.objects.get(user=request.user)

                print('Книга:', book)
                print('Профиль пользователя:', profile)

                # Добавляем книгу в ManyToManyField `purchased_books`
                profile.purchased_books.add(book)

                # Сохраняем изменения в профиле
                profile.save()

                print('Купленные книги:', profile.purchased_books.all())  # Отладочный вывод

                return render(request, 'subscription/completed.html', {'book': book})

        except stripe.error.StripeError as e:
            # Обработка ошибок Stripe
            print('Ошибка Stripe:', str(e))
            return render(request, 'subs/error.html', {'error': str(e)})
        except Profile.DoesNotExist:
            print('Профиль не найден для пользователя:', request.user)
            return redirect('subs:canceled')
        except Exception as e:
            print('Общая ошибка:', str(e))
            return redirect('subs:canceled')

    print('Сессия или ID книги отсутствуют, перенаправление на отмену')
    return redirect('subs:canceled')
