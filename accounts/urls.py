from django.urls import path
from .views import (
    UserLoginView, UserRegistrationView, UserRegistrationDoneView,
    VerifyEmailView, EmailCheckView, edit, UserLogoutView, profile_view,
    CustomPasswordResetView, CustomPasswordChangeView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView,
    RegisterView, LoginView, LogoutView, ProfileUpdateView,
    PasswordChangeView, PasswordResetView, SetNewPasswordView, VerifyEmailApi,
)

urlpatterns = [
    # Django views
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('register/done/', UserRegistrationDoneView.as_view(), name='register_done'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('email/check/', EmailCheckView.as_view(), name='email_check'),
    path('edit/<int:id>/', edit, name='edit'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # DRF views
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/profile/update/', ProfileUpdateView.as_view(), name='api_profile_update'),
    path('api/password/change/', PasswordChangeView.as_view(), name='api_password_change'),
    path('api/password/reset/', PasswordResetView.as_view(), name='api_password_reset'),
    path('api/password/reset/confirm/<uidb64>/<token>/', SetNewPasswordView.as_view(), name='api_password_reset_confirm'),
    path('api/email/verify/<uidb64>/<token>/', VerifyEmailApi.as_view(), name='api_verify_email'),
]
