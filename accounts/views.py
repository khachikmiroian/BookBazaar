from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from rest_framework import viewsets

from .forms import (
    LoginForm,
    UserRegistrationForm,
    UserEditForm,
    ProfileEditForm
)
from .models import Profile, MyUser
from subscriptions.models import Subscription, BookPurchase
from .serializers import ProfileSerializer
from .tasks import (
    send_registration_email,
    send_profile_updated_email,
    send_password_change_email,
    send_password_reset_email
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

    context = {
        'user': user,
        'purchased_books': purchased_books,
        'active_subscription': active_subscription,
    }
    return render(request, 'accounts/profile.html', context)


class UserLoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            username_or_email = cd['username_or_email']
            password = cd['password']
            user = authenticate(request, username=username_or_email, password=password)

            if user is None:
                try:
                    user = MyUser.objects.get(email=username_or_email)
                except MyUser.DoesNotExist:
                    try:
                        user = MyUser.objects.get(username=username_or_email)
                    except MyUser.DoesNotExist:
                        user = None

                if user and user.check_password(password):
                    login(request, user)
                else:
                    user = None

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('profile')
                else:
                    return redirect('login')
            else:
                return redirect('login')

        return render(request, 'accounts/login.html', {'form': form})


class UserRegistrationView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register_done')

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        Profile.objects.create(user=new_user)
        send_registration_email.delay(new_user.email, new_user.username)
        return super().form_valid(form)


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
    next_page = reverse_lazy('books:home')


class CustomPasswordResetView(View):
    def get(self, request):
        form = PasswordResetForm()
        return render(request, 'registration/password_reset.html', {'form': form})

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
            return render(request, 'registration/password_reset.html', {'form': form})


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
    success_url = reverse_lazy('password_reset_confirm.html')
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


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
