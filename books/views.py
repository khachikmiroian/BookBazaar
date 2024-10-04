from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView
from django.views.generic import DetailView
from accounts.models import Profile
from .models import Books, Author, Bookmarks, Comments
from subscriptions.models import BookPurchase, Subscription
from .forms import SearchForm, CommentsForm
from django.http import FileResponse, Http404, HttpResponse
from rest_framework import viewsets
from .serializers import BookSerializer
import requests
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator


class HomeView(TemplateView):
    template_name = 'books/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['random_quote'] = self.get_quote()
        return context

    def get_quote(self):
        request = requests.get('https://favqs.com/api/qotd').json()
        return f'Daily quote:{request["quote"]["body"]}'


class AboutUsView(TemplateView):
    template_name = 'books/about_us.html'


def post_search(request):
    form = SearchForm()
    query = None
    book_results = []
    author_results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            book_results = Books.objects.filter(
                status=Books.Status.PUBLISHED,
                title__icontains=query
            ).distinct()

            author_results = Author.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).distinct()

    return render(request,
                  'search.html',
                  {'form': form,
                   'query': query,
                   'author_results': author_results,
                   'book_results': book_results})



class BookListView(ListView):
    model = Books
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 6  # Количество книг на странице

    def get_queryset(self):
        # Получаем книги со статусом 'PB'
        return Books.objects.filter(status='PB')

class BookListByTagView(ListView):
    model = Books
    template_name = 'books/book_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        tag_slug = self.kwargs.get('tag_slug')
        return Books.objects.filter(tags__slug=tag_slug, status='PB').prefetch_related('tags')


class AddBookmarkView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Books, id=pk)
        profile = get_object_or_404(Profile, user=request.user)

        # Проверяем, существует ли закладка
        bookmark, created = Bookmarks.objects.get_or_create(profile=profile, book=book)

        if not created:
            # Если закладка уже существует, то удаляем ее
            bookmark.delete()

        return redirect('books:book_detail', pk=pk)


class RemoveBookmarkView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Books, id=pk)
        profile = get_object_or_404(Profile, user=request.user)

        bookmark = get_object_or_404(Bookmarks, profile=profile, book=book)
        bookmark.delete()
        return redirect('books:book_detail', pk=pk)


class AuthorListView(ListView):
    model = Author
    template_name = 'books/author_list.html'
    paginate_by = 6


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'books/author_detail.html'


class BookDetailView(DetailView):
    model = Books
    template_name = 'books/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.get_object()
        context['form'] = CommentsForm()

        # Логика для работы с комментариями
        comments = context['book'].comments.all()
        context['comments'] = comments[:3]  # Показываем только первые 3 комментария
        context['all_comments'] = comments  # Для кнопки "Показать еще"
        context['show_all'] = len(comments) > 3  # Проверяем, есть ли еще комментарии

        # Логика для аутентификации пользователя
        if self.request.user.is_authenticated:
            purchased_books = BookPurchase.objects.filter(user=self.request.user).values_list('book_id', flat=True)
            subscription = Subscription.objects.filter(user=self.request.user, end_date__gt=timezone.now()).exists()
            context['has_active_subscription'] = subscription
            context['purchased_books'] = purchased_books
            context['has_purchased'] = context['book'].id in purchased_books
            context['can_purchase'] = context['book'].id not in purchased_books

            # Проверка, добавлена ли книга в закладки
            context['bookmarked'] = Bookmarks.objects.filter(profile=self.request.user.profile,
                                                             book=context['book']).exists()
        else:
            context['purchased_books'] = []
            context['has_active_subscription'] = False
            context['can_purchase'] = False
            context['has_purchased'] = False
            context['bookmarked'] = False

        return context

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        form = CommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.books = book
            comment.profile = request.user.profile
            comment.save()
            return self.get(request, *args, **kwargs)
        else:
            return self.get(request, *args, **kwargs)

    def delete_comment(self, request, comment_id):
        """Метод для удаления комментария."""
        try:
            comment = Comments.objects.get(id=comment_id, profile=request.user.profile)
            comment.delete()
            return redirect('books:book_detail',
                            pk=self.get_object().pk)  # Убедитесь, что у вас есть правильный URL для перенаправления
        except Comments.DoesNotExist:
            pass  # Обработка случая, когда комментарий не найден


def view_pdf(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if book.pdf_file:
        response = FileResponse(book.pdf_file.open(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(book.pdf_file.name)
        return response
    raise Http404("PDF file not found")


def view_pdf_in_new_tab(request, book_id):
    book = get_object_or_404(Books, id=book_id)

    if not book.pdf_file:
        return HttpResponse('PDF not available', status=404)

    # Отображаем отдельную страницу с PDF через PDF.js
    return render(request, 'books/view_pdf.html', {'book': book})


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer


def delete_comment(request, comment_id):  # Используйте id здесь, чтобы соответствовать URL
    if request.method == 'POST':
        comment = get_object_or_404(Comments, pk=comment_id)
        book_id = comment.books.id  # Сохраняем id книги перед удалением
        comment.delete()
        return redirect('books:book_detail', pk=book_id)  # Перенаправление на страницу книги
    return redirect('books:book_list')  # Или куда-то еще в случае GET-запроса


def update_comment(request, comment_id):
    comment = get_object_or_404(Comments, id=comment_id)
    if request.method == 'POST':
        comment.content = request.POST['content']
        comment.save()
        # Можно добавить flash-сообщение для успешного редактирования
    return redirect('books:book_detail', pk=comment.books.id)


def load_more_comments(request, book_id):
    if request.is_ajax():
        book = get_object_or_404(Books, id=book_id)
        comments = book.comments.all()

        # Paginate comments
        paginator = Paginator(comments, 3)  # Show 3 comments per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        comments_data = []
        for comment in page_obj:
            comments_data.append({
                'username': comment.profile.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_modified': comment.is_modified,
            })

        return JsonResponse({'comments': comments_data})
    return JsonResponse({'comments': []})
