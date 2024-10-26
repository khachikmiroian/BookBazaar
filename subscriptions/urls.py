from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionsList, SubscriptionView, create_subscription_session,
    create_book_purchase_session, payment_completed, payment_canceled,
    SubscriptionViewSet
)
from . import webhook

router = DefaultRouter()
router.register(r'api/subscriptions', SubscriptionViewSet, basename='subscriptions')

app_name = 'subscriptions'

urlpatterns = [
    # Django views
    path('', SubscriptionsList.as_view(), name='subscriptions_list'),
    path('subscription/<int:pk>/', SubscriptionView.as_view(), name='subscription_detail'),
    path('create-subscription-session/<int:plan_id>/', create_subscription_session, name='create_subscription_session'),
    path('create-book-purchase-session/<int:book_id>/', create_book_purchase_session,
         name='create_book_purchase_session'),
    path('completed/', payment_completed, name='completed'),
    path('canceled/', payment_canceled, name='canceled'),
    path('webhook/', webhook.stripe_webhook, name='stripe_webhook'),

    # DRF views
    path('', include(router.urls)),
]
