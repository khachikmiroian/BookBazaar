from django.db import models
from books.models import Books
from django.utils import timezone
from subscriptions.models import Subscription


class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=35)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_of_birth = models.DateField(blank=True, null=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    purchased_books = models.ManyToManyField(Books, related_name='purchasers', blank=True)
    bookmarks = models.ManyToManyField(Books, related_name='bookmarked_by', blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

    def get_active_subscription(self):
        return Subscription.objects.filter(user=self.user, end_date__gt=timezone.now()).first()
