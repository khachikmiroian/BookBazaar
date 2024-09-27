from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.contrib.auth.views import LogoutView, PasswordResetView
from django.urls import reverse_lazy
from rest_framework import viewsets
from .serializers import ProfileSerializer
from subscriptions.models import Subscription, BookPurchase
from .tasks import send_registration_email, send_profile_updated_email, send_password_change_email, send_password_reset_email
from django.contrib.auth.views import PasswordChangeView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


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
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
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


class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        user_email = form.cleaned_data['email']
        users = form.get_users(user_email)

        response = super().form_valid(form)

        if users:
            user = users[0]
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            send_password_reset_email.delay(user_email, uid, token, user.username)

        return response


class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)

        user = form.user
        username = user.username
        user_email = user.email

        send_password_change_email.delay(user_email, username)

        return response

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
