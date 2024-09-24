from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import FileResponse, Http404
from django.conf import settings
import stripe
from .models import Books, Author
from subscriptions.models import BookPurchase
from .forms import SearchForm
from rest_framework import viewsets
from .serializers import BookSerializer
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Главная страница
class HomeView(TemplateView):
    template_name = 'books/home.html'


# О нас
class AboutUsView(TemplateView):
    template_name = 'books/about_us.html'


# Поиск книг и авторов
def post_search(request):
    form = SearchForm()
    query = None
    book_results = []
    author_results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # Логирование поиска
            logger.info(f'Поисковый запрос: {query}')

            # Поиск книг
            book_results = Books.objects.filter(
                status=Books.Status.PUBLISHED,
                title__icontains=query
            ).distinct()

            # Поиск авторов
            author_results = Author.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).distinct()

    return render(request, 'search.html', {
        'form': form,
        'query': query,
        'author_results': author_results,
        'book_results': book_results
    })


# Список книг с пагинацией
class BookListView(ListView):
    model = Books
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 6

    def get_queryset(self):
        queryset = Books.objects.filter(status='PB')
        # Логирование списка книг
        logger.info('Загружен список книг')
        return queryset


# Список авторов с пагинацией
class AuthorListView(ListView):
    model = Author
    template_name = 'books/author_list.html'
    paginate_by = 6


# Детали автора
class AuthorDetailView(DetailView):
    model = Author
    template_name = 'books/author_detail.html'


# Детали книги (только для авторизованных пользователей)
@method_decorator(login_required, name='dispatch')
class BookDetailView(DetailView):
    model = Books
    template_name = 'books/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.get_object()
        # Логирование деталей книги
        logger.info(f'Пользователь {self.request.user.username} просмотрел книгу {context["book"].title}')
        return context


# Контактная страница
class Contact(TemplateView):
    template_name = 'books/contact.html'


# Просмотр PDF-файла книги
def view_pdf(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if book.pdf_file:
        # Логирование попытки открытия PDF
        logger.info(f'Пользователь {request.user.username} открыл PDF файл книги {book.title}')
        response = FileResponse(book.pdf_file.open(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{book.pdf_file.name}"'
        return response
    # Логирование ошибки, если файл не найден
    logger.error(f'PDF файл для книги {book.title} не найден')
    raise Http404("PDF file not found")


# ViewSet для книг
class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
    logger.info('Загружен ViewSet для книг')
