from django.urls import path, include
from .views import *
from subscriptions.views import create_subscription_session
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import BookViewSet

app_name = 'books'
router = DefaultRouter()
router.register(r'books-api', BookViewSet) 

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('search/', post_search, name='search'),
    path('about-us/', AboutUsView.as_view(), name='about_us'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),
    path('view-pdf/<int:book_id>/', view_pdf, name='view_pdf'),
    path('api/', include(router.urls)),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

