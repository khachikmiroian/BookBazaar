from django.urls import path, include
from . import views


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.register, name='register'),
    path('edit/<int:id>/', views.edit, name='edit'),

]
