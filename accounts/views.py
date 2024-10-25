from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone  # Не забудьте импортировать timezone

from .forms import (
    LoginForm,
    UserRegistrationForm,
    UserEditForm,
    ProfileEditForm
)
from .models import Profile, MyUser
from subscriptions.models import Subscription, BookPurchase
from .tasks import (
    send_profile_updated_email,
    send_password_change_email,
    send_password_reset_email,
    send_verification_email
)
from django.contrib.auth.forms import (
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.views import LogoutView, PasswordChangeView


@login_required
def profile_view(request):
    user = request.user
    purchased_books = BookPurchase.objects.filter(user=user)

    active_subscription = getattr(user, 'subscription', None)
    if active_subscription and not active_subscription.is_active:
        active_subscription = None

    return render(request, 'accounts/profile.html', {
        'user': user,
        'purchased_books': purchased_books,
        'active_subscription': active_subscription,
    })


class UserLoginView(View):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username_or_email, password=password)

            if user is not None:

                if not user.is_active:
                    form.add_error(None,
                                   'Your email address is not verified. Please check your email to verify your account.')
                    return render(request, self.template_name, {'form': form})

                login(request, user)
                return redirect('profile')
            else:
                form.add_error(None, 'Invalid username or password.')

        return render(request, self.template_name, {'form': form})


class UserRegistrationView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('email_check')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        existing_user = MyUser.objects.filter(email=email).first()

        if existing_user:
            if not existing_user.email_verified_at:
                form.add_error('email',
                               'This email is already registered but not verified. Please check your email to verify your account.')
                return self.form_invalid(form)

        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.is_active = False
        new_user.email_verified_at = None
        new_user.save()

        Profile.objects.create(user=new_user)

        send_verification_email.delay(new_user.id)

        messages.success(self.request, 'Registration successful! Please check your email to complete the registration.')
        return super().form_valid(form)


class EmailCheckView(View):
    template_name = 'accounts/email_check.html'

    def get(self, request):
        return render(request, self.template_name)


class VerifyEmailView(View):
    def get(self, request, uidb64):
        try:
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = MyUser.objects.get(id=user_id)

            if user.is_active:
                return HttpResponse('Email has already been verified.')

            user.is_active = True
            user.email_verified_at = timezone.now()
            user.save()

            messages.success(request, 'Your email has been verified! You can now log in.')
            return redirect('register_done')

        except MyUser.DoesNotExist:
            return HttpResponse('Invalid verification link.')


class UserRegistrationDoneView(View):
    def get(self, request):
        return render(request, 'accounts/register_done.html', {'new_user': request.user})


@login_required
def edit(request, id):
    profile = get_object_or_404(Profile, user_id=id)

    if request.user.id != profile.user_id:
        return redirect('profile')

    if request.method == 'POST':
        user_form = UserEditForm(instance=profile.user, data=request.POST)
        profile_form = ProfileEditForm(instance=profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            send_profile_updated_email.delay(profile.user.email, profile.user.username)
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=profile.user)
        profile_form = ProfileEditForm(instance=profile)

    return render(request, 'accounts/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    })


class UserLogoutView(LogoutView):
    template_name = 'logged_out.html'
    next_page = reverse_lazy('home')


class CustomPasswordResetView(View):
    def get(self, request):
        form = PasswordResetForm()
        return render(request, 'registration/password_reset.html', {'form': form})  # Исправлено

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = MyUser.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                send_password_reset_email.delay(email, uid, token, user.username)
                return redirect('password_reset_done')
        return render(request, 'registration/password_reset.html', {'form': form})  # Исправлено


class CustomPasswordResetDoneView(View):
    def get(self, request):
        return render(request, 'registration/password_reset_done.html')


class CustomPasswordResetConfirmView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = MyUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user=user)
        else:
            form = None

        return render(request, 'registration/password_reset_confirm.html', {'form': form})

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = MyUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_complete')
        else:
            form = SetPasswordForm(user=user)

        return render(request, 'registration/password_reset_confirm.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('password_reset_complete')
    form_class = PasswordChangeForm

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, 'Password was successfully changed.')
        send_password_change_email.delay(user.email, user.username)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'An error occurred while changing the password.')
        return super().form_invalid(form)


class CustomPasswordResetCompleteView(View):
    def get(self, request):
        return render(request, 'registration/password_reset_complete.html')
