from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView
from django.views.generic import DetailView
from accounts.models import Profile
from .models import Books, Author, Bookmarks
from subscriptions.models import BookPurchase, Subscription
from .forms import SearchForm, CommentsForm
from django.http import FileResponse, Http404, HttpResponse
from rest_framework import viewsets
from .serializers import BookSerializer
import requests
from django.utils import timezone


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
    paginate_by = 6

    def get_queryset(self):
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

        Bookmarks.objects.get_or_create(profile=profile, book=book)
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

        if self.request.user.is_authenticated:
            purchased_books = BookPurchase.objects.filter(user=self.request.user).values_list('book_id', flat=True)
            subscription = Subscription.objects.filter(user=self.request.user, end_date__gt=timezone.now()).exists()
            context['has_active_subscription'] = subscription
            context['purchased_books'] = purchased_books
            context['has_purchased'] = context['book'].id in purchased_books
            context['can_purchase'] = context['book'].id not in purchased_books
            context['bookmarked'] = Bookmarks.objects.filter(profile=self.request.user.profile,
                                                             book=context['book']).exists()
        else:
            context['purchased_books'] = []
            context['has_active_subscription'] = False
            context['can_purchase'] = False
            context['has_purchased'] = False
            context['bookmarked'] = False
        context['comments'] = context['book'].comments.all()
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


class Contact(TemplateView):
    template_name = 'books/contact.html'


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
