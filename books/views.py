from django.db.models import Q
from django.shortcuts import render
# from django.contrib.postgres.search import SearchVector, SearchQuery, TrigramSimilarity
from .forms import SearchForm
from .models import Books, Author
from django.views.generic import TemplateView, ListView, DetailView


class HomeView(TemplateView):
    template_name = 'books/home.html'


class AboutUsView(TemplateView):
    template_name = 'books/about_us.html'


# def post_search(request):
#     form = SearchForm()
#     query = None
#     book_results = []  # Инициализация переменной book_results
#     author_results = []  # Инициализация переменной author_results
#
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#
#             # # Поиск книг
#             # book_search_vector = SearchVector('title', weight='A')
#             # book_search_query = SearchQuery(query)
#             book_results = Books.objects.filter(status=Books.Status.PUBLISHED).annotate(
#                 similarity=TrigramSimilarity('title', query),
#             ).filter(similarity__gt=0.1).order_by('-similarity')
#
#             # # Поиск авторов
#             # author_search_vector = SearchVector('name', weight='A')
#             # author_search_query = SearchQuery(query)
#             author_results = Author.objects.annotate(
#                 similarity=TrigramSimilarity('first_name', query),
#             ).filter(similarity__gt=0.1).order_by('-similarity')
#
#             author_results = author_results.distinct()
#             book_results = book_results.distinct()
#
#     return render(request,
#                   'search.html',
#                   {'form': form,
#                    'query': query,
#                    'author_results': author_results,
#                    'book_results': book_results})

def post_search(request):
    form = SearchForm()
    query = None
    book_results = []
    author_results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            # Поиск книг
            book_results = Books.objects.filter(
                status=Books.Status.PUBLISHED,
                title__icontains=query
            ).distinct()

            # Поиск авторов
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
    paginate_by = 6


class AuthorListView(ListView):
    model = Author
    template_name = 'books/author_list.html'
    paginate_by = 6


class BookDetailView(DetailView):
    model = Books
    template_name = 'books/book_detail.html'


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'books/author_detail.html'


class Contact(TemplateView):
    template_name = 'books/contact.html'
