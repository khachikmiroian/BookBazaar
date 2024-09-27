from django.db import models
from django.conf import settings
from books.models import Books
from django.utils import timezone
from subscriptions.models import Subscription


class Profile(models.Model):
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    purchased_books = models.ManyToManyField(Books, related_name='purchasers', blank=True)
    bookmarks = models.ManyToManyField(Books, related_name='bookmarked_by', blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

    def get_active_subscription(self):
        return Subscription.objects.filter(user=self.user, end_date__gt=timezone.now()).first()
