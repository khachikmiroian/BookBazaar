import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView
from accounts.models import Profile
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import BookSerializer, AuthorSerializer, CommentsSerializer, BookmarksSerializer
from .permissions import IsOwnerOrReadOnly, IsSubscribedOrPurchased
from rest_framework.decorators import action
from .models import Books, Author, Bookmarks, Comments
from subscriptions.models import BookPurchase, Subscription
from .forms import SearchForm, CommentsForm
from django.urls import reverse
from django.http import FileResponse, Http404, JsonResponse, HttpResponse
import requests
from django.utils import timezone
from django.core.paginator import Paginator


class HomeView(TemplateView):
    template_name = 'books/home.html'


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
            book_results = Books.objects.filter(
                status=Books.Status.PUBLISHED,
                title__icontains=query
            ).distinct()
            author_results = Author.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            ).distinct()

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
            return redirect(self.get_object())

        return self.get(request, *args, **kwargs)


class AddCommentView(LoginRequiredMixin, FormView):
    form_class = CommentsForm
    template_name = 'books/book_detail.html'

    def form_valid(self, form):
        book = get_object_or_404(Books, id=self.kwargs['book_id'])
        comment = form.save(commit=False)
        comment.books = book
        comment.profile = self.request.user.profile
        comment.save()
        return redirect('books:book_detail', pk=book.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Books, id=self.kwargs['book_id'])
        context['comments'] = context['book'].comments.all()[:3]
        context['show_all'] = context['book'].comments.count() > 3
        return context


class DeleteCommentView(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comments, id=comment_id, profile=request.user.profile)
        book_id = comment.books.id
        comment.delete()
        return redirect('books:book_detail', pk=book_id)


class UpdateCommentView(LoginRequiredMixin, FormView):
    form_class = CommentsForm
    template_name = 'books/book_detail.html'

    def form_valid(self, form):
        comment = get_object_or_404(Comments, id=self.kwargs['comment_id'], profile=self.request.user.profile)
        comment.content = form.cleaned_data['content']
        comment.save()
        return redirect('books:book_detail', pk=comment.books.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Books, id=self.kwargs['book_id'])
        context['comments'] = context['book'].comments.all()[:3]
        context['show_all'] = context['book'].comments.count() > 3
        context['editing_comment'] = get_object_or_404(Comments, id=self.kwargs['comment_id'],
                                                       profile=self.request.user.profile)
        return context


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


class BookmarksView(LoginRequiredMixin, ListView):
    model = Bookmarks
    template_name = 'books/bookmarks.html'
    context_object_name = 'bookmarks'

    def get_queryset(self):
        profile = self.request.user.profile
        return Bookmarks.objects.filter(profile=profile).select_related('book')


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    queryset = Author.objects.all()


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='purchase')
    def purchase_book(self, request, pk=None):
        book = self.get_object()
        user = request.user
        if BookPurchase.objects.filter(user=user, book=book).exists():
            return Response(
                {"message": "You already own this book."},
                status=status.HTTP_400_BAD_REQUEST
            )

        success_url = request.build_absolute_uri('/subscriptions/completed/')
        cancel_url = request.build_absolute_uri('/subscriptions/canceled/')

        session_data = {
            'payment_method_types': ['card'],
            'customer_email': user.email,
            'line_items': [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': book.title,
                    },
                    'unit_amount': int(book.price * 100),
                },
                'quantity': 1,
            }],
            'mode': 'payment',
            'success_url': success_url + '?session_id={CHECKOUT_SESSION_ID}',
            'cancel_url': cancel_url,
            'metadata': {
                'purchase_type': 'book',
                'item_id': book.id
            }
        }

        try:

            session = stripe.checkout.Session.create(**session_data)
            return Response({'checkout_url': session.url}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsSubscribedOrPurchased],
            url_path='pdf-url')
    def get_pdf_url(self, request, pk=None):
        book = self.get_object()
        if book.pdf_file:
            pdf_url = request.build_absolute_uri(reverse('books:view_pdf_in_new_tab', args=[book.id]))
            return Response({'pdf_url': pdf_url}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "PDF file doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='comments/add')
    def add_comment(self, request, pk=None):
        book = self.get_object()
        content = request.data.get('content', '')
        if not content:
            return Response({"error": "Comment cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comments.objects.create(books=book, profile=request.user.profile, content=content)
        serializer = CommentsSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly],
            url_path='comments/(?P<comment_id>[^/.]+)/edit')
    def update_comment(self, request, pk=None, comment_id=None):

        comment = get_object_or_404(Comments, id=comment_id, books_id=pk, profile=request.user.profile)

        serializer = CommentsSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsOwnerOrReadOnly],
            url_path='comments/(?P<comment_id>[^/.]+)/remove')
    def delete_comment(self, request, pk=None, comment_id=None):
        comment = get_object_or_404(Comments, id=comment_id, books_id=pk, profile=request.user.profile)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='add-bookmark')
    def add_bookmark(self, request, pk):
        book = self.get_object()

        bookmark, created = Bookmarks.objects.get_or_create(profile=request.user.profile, book=book)
        if not created:
            return Response(
                {"message": "Book already in bookmarks."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = BookmarksSerializer(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated], url_path='remove-bookmark')
    def remove_bookmark(self, request, pk):
        book = self.get_object()
        bookmark = Bookmarks.objects.filter(profile=request.user.profile, book=book).first()
        if not bookmark:
            return Response(
                {"error": "Book doesn't exists in bookmarks."},
                status=status.HTTP_404_NOT_FOUND
            )

        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
