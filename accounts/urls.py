from django.urls import path, include
from . import views
app_name = 'accounts'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.register, name='register'),
    path('edit/<int:id>/', views.edit, name='edit'),
]
