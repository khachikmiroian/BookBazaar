import random
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_registration_email(user_email, username):
    subject = 'Welcome to our Library!'
    message = (f'Dear {username}, thank you for registering in our Library Site, '
               f'We hope you enjoy our site!')
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result


@shared_task
def send_profile_updated_email(user_email, username):
    subject = 'Your Profile successufuly updated'
    message = f'Dear {username}, your profile successfully updated'
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result


@shared_task
def send_password_reset_email(user_email, uid, token, username):
    subject = 'Your password reset request'
    message = (
        f'Someone asked for a password reset for the email {user_email}.\n\n'
        f'Follow the link below to reset your password:\n'
        f'{settings.PROTOCOL}://{settings.DOMAIN}/{settings.RESET_URL}/{uid}/{token}/\n\n'
        f'Your username, in case you\'ve forgotten: {username}'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result


@shared_task
def send_password_change_email(user_email, username):
    subject = 'Password changed succesfully !'
    message = f'Dear {username}, your password changed successfully!'
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result
