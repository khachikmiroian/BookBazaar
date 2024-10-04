from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_purchase_email(user_email, purchase_type, item_name, username):
    try:
        if purchase_type == 'subscription':
            subject = 'Your Subscription Details'
            message = f'Dear {username}, thank you for subscribing to our {item_name} plan!'
            from_email = settings.DEFAULT_FROM_EMAIL
            return send_mail(subject, message, from_email, [user_email])

        elif purchase_type == 'book':
            subject = 'Your Book Purchase'
            message = f'Dear {username}, thank you for purchasing the book: {item_name}. We hope you enjoy it!'
            from_email = settings.DEFAULT_FROM_EMAIL
            return send_mail(subject, message, from_email, [user_email])

        return None

    except Exception as e:
        return None
