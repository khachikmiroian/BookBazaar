from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.post_search, name='search'),
    path('about/', views.AboutUsView.as_view(), name='about_us'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('authors/', views.AuthorListView.as_view(), name='author_list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail')
]
