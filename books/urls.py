from django.urls import path
from .views import BookDetailView, BookListView, AuthorListView, AuthorDetailView, HomeView, AboutUsView, success_view, \
    canceled_view
from subscriptions.views import create_subscription_session

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
    path('create-subscription-session/<int:plan_id>/', create_subscription_session, name='create_subscription_session'),
    # Другие пути
]
