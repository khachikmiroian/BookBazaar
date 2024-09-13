from django.urls import path, include
from . import views

app_name = 'subs'

urlpatterns = [
    path('subscriptions-list/', views.SubscriptionsList.as_view(), name='subscriptions_list'),
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
]