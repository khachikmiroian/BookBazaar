from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views.generic import TemplateView, ListView
from django.conf import settings
from books.models import Books
import stripe
from .models import SubscriptionPlan

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
        context['subscription'] = SubscriptionPlan.objects.get(pk=self.kwargs['pk'])
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


@login_required
def create_subscription_session(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('subs:completed'))
        cancel_url = request.build_absolute_uri(reverse('subs:canceled'))

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
            'metadata': {
                'purchase_type': 'subscription',
                'plan_name': plan.name
            }
        }

        session = stripe.checkout.Session.create(**session_data)

        return redirect(session.url, code=303)
    else:
        return render(request, 'subscription/subscribe.html', {'plan': plan})


def payment_completed(request):
    return render(request, 'subscription/completed.html')


def payment_canceled(request):
    return render(request, 'subscription/canceled.html')


@login_required
def create_book_purchase_session(request, book_id):
    book = get_object_or_404(Books, id=book_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('subs:completed'))
        cancel_url = request.build_absolute_uri(reverse('subs:canceled'))

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
            'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': cancel_url,
            'metadata': {
                'purchase_type': 'book',
                'item_id': book.id
            }
        }

        session = stripe.checkout.Session.create(**session_data)

        return redirect(session.url, code=303)
    else:
        return render(request, 'books/book_detail.html', {'book': book})

