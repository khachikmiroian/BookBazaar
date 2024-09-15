from django.urls import path
from . import views

app_name = 'subs'

urlpatterns = [
    path('subscriptions-list/', views.SubscriptionsList.as_view(), name='subscriptions_list'),
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('process/', views.payment_process, name='process'),
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/', views.payment_canceled, name='canceled'),
]
