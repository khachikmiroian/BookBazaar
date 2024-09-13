from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.postgres.search import SearchVector, SearchQuery, TrigramSimilarity
from .forms import SearchForm
from .models import Books, Author
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.views import LoginView
class HomeView(TemplateView):
    template_name = 'books/home.html'


class AboutUsView(TemplateView):
    template_name = 'books/about_us.html'


@login_required
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            book_search_vector = SearchVector('title', weight='A')
            book_search_query = SearchQuery(query)
            book_results = Books.objects.filter(status=Books.Status.PUBLISHED).annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

            author_search_vector = SearchVector('name', weight='A')
            author_search_query = SearchQuery(query)
            author_results = Author.objects.annotate(
                similarity=TrigramSimilarity('name', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

            author_results = author_results.distinct()
            book_results = book_results.distinct()

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
