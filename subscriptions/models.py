from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = (
        ('M', 'By month'),
        ('Y', 'By year')
    )
    name = models.CharField(max_length=20, choices=PLAN_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('subscriptions:subscription_detail', args=[str(self.id)])


class Subscription(models.Model):
    user = models.OneToOneField('accounts.MyUser', on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    @property
    def is_active(self):
        return self.end_date > timezone.now()

    def save(self, *args, **kwargs):
        if not self.end_date:
            if self.plan and self.plan.name == 'M':
                self.end_date = self.start_date + timedelta(days=30)
            elif self.plan and self.plan.name == 'Y':
                self.end_date = self.start_date + timedelta(days=365)
        super().save(*args, **kwargs)


class BookPurchase(models.Model):
    user = models.ForeignKey('accounts.MyUser', on_delete=models.CASCADE)
    book = models.ForeignKey('books.Books', on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f'{self.user.username} bought {self.book.title}'
