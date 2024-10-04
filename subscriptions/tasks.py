from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_purchase_email(user_email, purchase_type, item_name, username):
    print(
        f'Starting send_purchase_email for {user_email}, purchase_type: {purchase_type}, item_name: {item_name}, username: {username}')

    try:
        if purchase_type == 'subscription':
            subject = 'Your Subscription Details'
            message = f'Dear {username}, thank you for subscribing to our {item_name} plan!'
            from_email = settings.DEFAULT_FROM_EMAIL

            print(f'Preparing to send subscription email to {user_email}')
            result = send_mail(subject, message, from_email, [user_email])
            print(f'Email sent to {user_email} for subscription: {result}')
            return result

        elif purchase_type == 'book':
            subject = 'Your Book Purchase'
            message = f'Dear {username}, thank you for purchasing the book: {item_name}. We hope you enjoy it!'
            from_email = settings.DEFAULT_FROM_EMAIL

            print(f'Preparing to send book purchase email to {user_email}')
            result = send_mail(subject, message, from_email, [user_email])
            print(f'Email sent to {user_email} for book: {result}')
            return result

        else:
            print(f'Invalid purchase_type: {purchase_type}')
            return None

    except Exception as e:
        print(f'Error sending email: {e}')
        return None