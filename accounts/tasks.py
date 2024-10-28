from celery import shared_task
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from .models import MyUser


@shared_task
def send_verification_email(user_id):
    user = MyUser.objects.get(id=user_id)
    uidb64 = urlsafe_base64_encode(force_bytes(user.id))
    token = default_token_generator.make_token(user)
    verification_link = f"{settings.PROTOCOL}://{settings.DOMAIN}/accounts/verify-email/{uidb64}/{token}/"

    subject = 'Verify your email address'
    message = (f'Dear {user.username},\n\n'
               f'Please verify your email address by clicking the link below:\n'
               f'{verification_link}\n\n'
               f'This link will expire in 20 minutes.')
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user.email])
    return result


@shared_task
def send_verification_email_for_drf(user_id):
    user = MyUser.objects.get(id=user_id)
    uidb64 = urlsafe_base64_encode(force_bytes(user.id))
    token = default_token_generator.make_token(user)
    verification_link = f"{settings.PROTOCOL}://{settings.DOMAIN}/accounts/api/email/verify/{uidb64}/{token}/"

    subject = 'Verify your email address'
    message = (f'Dear {user.username},\n\n'
               f'Please verify your email address by clicking the link below:\n'
               f'{verification_link}\n\n'
               f'This link will expire in 20 minutes.')
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user.email])
    return result


@shared_task
def send_registration_email(user_email, username):
    subject = 'Welcome to our Library!'
    message = (f'Dear {username}, thank you for registering at our Library Site. '
               f'We hope you enjoy our site!')
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result


@shared_task
def send_profile_updated_email(user_email, username):
    subject = 'Your Profile Has Been Successfully Updated'
    message = f'Dear {username}, your profile has been successfully updated.'
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result


@shared_task
def send_password_reset_email(user_email, uid, token, username):
    subject = 'Your Password Reset Request'
    message = (
        f'Someone requested a password reset for the email {user_email}.\n\n'
        f'Follow the link below to reset your password:\n'
        f'{settings.PROTOCOL}://{settings.DOMAIN}{settings.RESET_URL}/{uid}/{token}/\n\n'
        f'Your username, in case you\'ve forgotten: {username}'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result


@shared_task
def send_password_reset_email_drf(user_email, uid, token, username):
    subject = 'Your Password Reset Request'
    message = (
        f'Someone requested a password reset for the email {user_email}.\n\n'
        f'Follow the link below to reset your password:\n'
        f'http://127.0.0.1:8000/accounts/api/password/reset/confirm/{uid}/{token}/\n\n'
        f'Your username, in case you\'ve forgotten: {username}'
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result


@shared_task
def send_password_change_email(user_email, username):
    subject = 'Password Changed Successfully!'
    message = f'Dear {username}, your password has been changed successfully!'
    from_email = settings.DEFAULT_FROM_EMAIL
    result = send_mail(subject, message, from_email, [user_email])
    return result


@shared_task
def delete_unverified_accounts():
    now = timezone.now()
    MyUser.objects.filter(is_active=False, date_joined__lt=now - timezone.timedelta(minutes=20)).delete()
