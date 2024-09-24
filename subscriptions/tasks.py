from celery import shared_task
from django.core.mail import send_mail
from .models import Subscription
from accounts.models import Profile
from django.conf import settings


@shared_task
def send_subscription_email(user_email, subscription_type):
    subject = 'Your Subscription Details'
    message = f'Dear {Profile.user.username} thank you for subscribing to our {subscription_type} plan'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user_email])
