from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HomeView, AboutUsView, post_search, BookListView, BookDetailView,
    BookListByTagView, AddBookmarkView, RemoveBookmarkView, AuthorListView,
    AuthorDetailView, view_pdf_in_new_tab, view_pdf, AddCommentView,
    UpdateCommentView, DeleteCommentView, load_more_comments, BookmarksView,
    BookViewSet, AuthorViewSet
)

router = DefaultRouter()
router.register(r'api/books', BookViewSet, basename='book')
router.register(r'api/authors', AuthorViewSet, basename='author')

app_name = 'books'

urlpatterns = [
    # Django views
    path('', BookListView.as_view(), name='book_list'),
    path('search/', post_search, name='search'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('tag/<slug:tag_slug>/', BookListByTagView.as_view(), name='book_list_by_tag'),
    path('books/<int:pk>/add_bookmark/', AddBookmarkView.as_view(), name='add_bookmark'),
    path('books/<int:pk>/remove_bookmark/', RemoveBookmarkView.as_view(), name='remove_bookmark'),
    path('authors/', AuthorListView.as_view(), name='author_list'),
    path('authors/<int:pk>/', AuthorDetailView.as_view(), name='author_detail'),
    path('view_pdf_in_new_tab/<int:book_id>/', view_pdf_in_new_tab, name='view_pdf_in_new_tab'),
    path('view_pdf_file/<int:book_id>/', view_pdf, name='view_pdf_file'),
    path('books/<int:book_id>/comment/add/', AddCommentView.as_view(), name='add_comment'),
    path('comment/edit/<int:comment_id>/', UpdateCommentView.as_view(), name='edit_comment'),
    path('comment/delete/<int:comment_id>/', DeleteCommentView.as_view(), name='delete_comment'),
    path('books/<int:book_id>/comment/update/<int:comment_id>/', UpdateCommentView.as_view(), name='update_comment'),
    path('books/load-more-comments/<int:book_id>/', load_more_comments, name='load_more_comments'),
    path('bookmarks/', BookmarksView.as_view(), name='bookmarks'),
    path('', HomeView.as_view(), name='home'),
    path('about-us/', AboutUsView.as_view(), name='about_us'),

    # DRF views
    path('', include(router.urls)),
]
