from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('register/done/', views.UserRegistrationDoneView.as_view(), name='register_done'),
    path('verify-email/<uidb64>/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('email/check/', views.EmailCheckView.as_view(), name='email_check'),
    path('edit/<int:id>/', views.edit, name='edit'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),  # Исправлено
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),  # Исправлено
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete.css'),
]
