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

# Убедитесь, что вы установили API-ключи Stripe
stripe.api_key = 'sk_test_51Q00p605q7WRrvT5jTfofvlcC0vR5IBnUVApJc3Vxy8lmVsFszMN3GLoLTiux0mL00XCm9VsUn6rbScf9ys89NX400FqEnX62P'


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
    context_object_name = 'books'
    paginate_by = 6

    def get_queryset(self):
        # Фильтруем только опубликованные книги
        return Books.objects.filter(status='PB')


class AuthorListView(ListView):
    model = Author
    template_name = 'books/author_list.html'
    paginate_by = 6


stripe.api_key = 'YOUR_STRIPE_SECRET_KEY'


@method_decorator(login_required, name='dispatch')
class BookDetailView(DetailView):
    model = Books
    template_name = 'books/book_detail.html'

    def post(self, request, *args, **kwargs):
        book = self.get_object()

        # Создание сессии Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': book.title,
                        },
                        'unit_amount': int(book.price * 100),  # Цена в центах
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse_lazy('books:success')),
            cancel_url=request.build_absolute_uri(reverse_lazy('books:canceled')),
        )

        # Сохранение покупки в модели BookPurchase
        BookPurchase.objects.create(user=request.user, book=book)

        return redirect(session.url, code=303)


class AuthorDetailView(DetailView):
    model = Author
    template_name = 'books/author_detail.html'


class Contact(TemplateView):
    template_name = 'books/contact.html'


# Представления для успешного и отмененного платежей
def success_view(request):
    return render(request, 'books/success.html')


def canceled_view(request):
    return render(request, 'books/canceled.html')
