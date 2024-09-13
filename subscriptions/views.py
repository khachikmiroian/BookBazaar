from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView


# Create your views here.
class SubscriptionsList(ListView):
    template_name = 'subscription/subscription_list.html'


class SubscriptionView(TemplateView):
    template_name = 'subscription/subscription_view.html'


class BookPurchase(TemplateView):
    template_name = 'subscription/bookpurchase.html'


def payment_process(request):
    pass


def payment_completed(request):
    pass


def payment_canceled(request):
    pass
