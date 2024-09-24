from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import stripe
from .models import Books, Author
from subscriptions.models import BookPurchase
from .forms import SearchForm
from django.http import FileResponse, Http404
from .models import Books
from django.conf import settings
from rest_framework import viewsets
from .models import Books
from .serializers import BookSerializer


class HomeView(TemplateView):
    template_name = 'books/home.html'


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
    paginate_by = 6

    def get_queryset(self):
        return Books.objects.filter(status='PB')


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

        if self.request.user.is_authenticated:
            purchased_books = BookPurchase.objects.filter(user=self.request.user).values_list('book_id', flat=True)
            context['purchased_books'] = purchased_books
        else:
            context['purchased_books'] = []

        return context


class Contact(TemplateView):
    template_name = 'books/contact.html'


def view_pdf(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if book.pdf_file:
        response = FileResponse(book.pdf_file.open(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(book.pdf_file.name)
        return response
    raise Http404("PDF file not found")


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
