from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from accounts.models import Profile
from .models import Books, Author, Bookmarks, Comments
from subscriptions.models import BookPurchase, Subscription
from .forms import SearchForm, CommentsForm
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
import requests
from django.utils import timezone
from django.core.paginator import Paginator


class HomeView(TemplateView):
    template_name = 'books/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['random_quote'] = self.get_quote()
        return context

    def get_quote(self):
        response = requests.get('https://favqs.com/api/qotd').json()
        return f'Daily quote: {response["quote"]["body"]}'


class AboutUsView(TemplateView):
    template_name = 'books/about_us.html'


def post_search(request):
    form = SearchForm()
    query = None
    book_results, author_results = [], []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            book_results = Books.objects.filter(status=Books.Status.PUBLISHED, title__icontains=query).distinct()
            author_results = Author.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query)).distinct()

    return render(request, 'search.html', {
        'form': form,
        'query': query,
        'author_results': author_results,
        'book_results': book_results
    })



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

        bookmark, created = Bookmarks.objects.get_or_create(profile=profile, book=book)
        if not created:
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
        comments = context['book'].comments.all()
        context['comments'] = comments[:3]
        context['all_comments'] = comments
        context['show_all'] = len(comments) > 3

        if self.request.user.is_authenticated:
            purchased_books = BookPurchase.objects.filter(user=self.request.user).values_list('book_id', flat=True)
            subscription = Subscription.objects.filter(user=self.request.user, end_date__gt=timezone.now()).exists()
            context['has_active_subscription'] = subscription
            context['purchased_books'] = purchased_books
            context['has_purchased'] = context['book'].id in purchased_books
            context['can_purchase'] = context['book'].id not in purchased_books
            context['bookmarked'] = Bookmarks.objects.filter(profile=self.request.user.profile, book=context['book']).exists()
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

    def delete_comment(self, request, comment_id):
        try:
            comment = Comments.objects.get(id=comment_id, profile=request.user.profile)
            comment.delete()
            return redirect('books:book_detail', pk=self.get_object().pk)
        except Comments.DoesNotExist:
            pass




def view_pdf(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if book.pdf_file:
        response = FileResponse(book.pdf_file.open(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{book.pdf_file.name}"'
        return response
    raise Http404("PDF file not found")


def view_pdf_in_new_tab(request, book_id):
    book = get_object_or_404(Books, id=book_id)
    if not book.pdf_file:
        return HttpResponse('PDF not available', status=404)
    return render(request, 'books/view_pdf.html', {'book': book})



def delete_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comments, pk=comment_id)
        book_id = comment.books.id
        comment.delete()
        return redirect('books:book_detail', pk=book_id)
    return redirect('books:book_list')


def update_comment(request, comment_id):
    comment = get_object_or_404(Comments, id=comment_id)
    if request.method == 'POST':
        comment.content = request.POST['content']
        comment.save()
    return redirect('books:book_detail', pk=comment.books.id)


def load_more_comments(request, book_id):
    if request.is_ajax():
        book = get_object_or_404(Books, id=book_id)
        comments = book.comments.all()
        paginator = Paginator(comments, 3)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        comments_data = [{
            'username': comment.profile.user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_modified': comment.is_modified,
        } for comment in page_obj]

        return JsonResponse({'comments': comments_data})
    return JsonResponse({'comments': []})


class BookmarksView(ListView):
    model = Bookmarks
    template_name = 'books/bookmarks.html'
    context_object_name = 'bookmarks'

    def get_queryset(self):
        # Get the current user's profile
        profile = self.request.user.profile
        # Return bookmarks for the logged-in user
        return Bookmarks.objects.filter(profile=profile).select_related('book')