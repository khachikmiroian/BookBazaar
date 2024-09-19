from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views.generic import TemplateView, ListView, DetailView
import stripe
from django.conf import settings
from .models import SubscriptionPlan
from books.models import Books


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

@login_required
def create_book_purchase_session(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if request.method == 'POST':
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=request.user.email,
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': book.title,
                    },
                    'unit_amount': int(book.price * 100),
                },
                'quantity': 1,
            }],
            metadata={
                'purchase_type': 'book',
                'item_id': book_id,
            },
            mode='payment',
            success_url=request.build_absolute_uri(reverse('subs:completed')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('subs:canceled'))
        )

        return JsonResponse({'id': session.id})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def payment_completed(request):
    return render(request, 'subscription/completed.html')


def payment_canceled(request):
    return render(request, 'subscription/canceled.html')
