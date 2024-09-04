from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('accounts.urls', namespace='accounts')),
    # path('books/', include('books.urls', namespace='books')),
    # path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
]
