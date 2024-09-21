from django.urls import path
from .views import *
from subscriptions.views import create_subscription_session
from django.conf import settings
from django.conf.urls.static import static

app_name = 'books'

urlpatterns = [
                  path('', HomeView.as_view(), name='home'),
                  path('about-us/', AboutUsView.as_view(), name='about_us'),
                  path('books/', BookListView.as_view(), name='book_list'),
                  path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
                  path('authors/', AuthorListView.as_view(), name='author_list'),
                  path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),
                  path('success/', success_view, name='success'),
                  path('canceled/', canceled_view, name='canceled'),
                  path('create-subscription-session/<int:plan_id>/', create_subscription_session,
                       name='create_subscription_session'),
                  path('view-pdf/<int:book_id>/', view_pdf, name='view_pdf'),  # Другие пути
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
