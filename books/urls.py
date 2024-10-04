from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

app_name = 'books'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('search/', post_search, name='search'),
    path('about-us/', AboutUsView.as_view(), name='about_us'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('tag/<slug:tag_slug>/', BookListByTagView.as_view(), name='book_list_by_tag'),
    path('books/<int:pk>/add_bookmark/', AddBookmarkView.as_view(), name='add_bookmark'),
    path('books/<int:pk>/remove_bookmark/', RemoveBookmarkView.as_view(), name='remove_bookmark'),
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),
    path('view_pdf_in_new_tab/<int:book_id>/', view_pdf_in_new_tab, name='view_pdf_in_new_tab'),
    path('view_pdf_file/<int:book_id>/', view_pdf, name='view_pdf_file'),
    path('comment/delete/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('comment/update/<int:comment_id>/', update_comment, name='update_comment'),
    path('books/load-more-comments/<int:book_id>/', load_more_comments, name='load_more_comments'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
