from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'books'

urlpatterns = [
                  path('', views.BookListView.as_view(), name='book_list'),
                  path('search/', views.post_search, name='search'),
                  path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
                  path('tag/<slug:tag_slug>/', views.BookListByTagView.as_view(), name='book_list_by_tag'),
                  path('books/<int:pk>/add_bookmark/', views.AddBookmarkView.as_view(), name='add_bookmark'),
                  path('books/<int:pk>/remove_bookmark/', views.RemoveBookmarkView.as_view(), name='remove_bookmark'),
                  path('authors/', views.AuthorListView.as_view(), name='author_list'),
                  path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
                  path('view_pdf_in_new_tab/<int:book_id>/', views.view_pdf_in_new_tab, name='view_pdf_in_new_tab'),
                  path('view_pdf_file/<int:book_id>/', views.view_pdf, name='view_pdf_file'),
                  path('books/<int:book_id>/comment/add/', views.AddCommentView.as_view(), name='add_comment'),
                  path('comment/edit/<int:comment_id>/', views.UpdateCommentView.as_view(), name='edit_comment'),
                  path('comment/delete/<int:comment_id>/', views.DeleteCommentView.as_view(), name='delete_comment'),
                  path('books/<int:book_id>/comment/update/<int:comment_id>/', views.UpdateCommentView.as_view(),
                       name='update_comment'),
                  path('books/load-more-comments/<int:book_id>/', views.load_more_comments, name='load_more_comments'),
                  path('bookmarks/', views.BookmarksView.as_view(), name='bookmarks'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
