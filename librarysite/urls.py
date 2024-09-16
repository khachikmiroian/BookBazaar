from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from books.views import Contact, AboutUsView, HomeView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('books/', include('books.urls', namespace='books')),
    path('subscriptions/', include('subscriptions.urls', namespace='subs')),
    path('contact/', Contact.as_view(), name='contact'),
    path('about-us/', AboutUsView.as_view(), name='about'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
