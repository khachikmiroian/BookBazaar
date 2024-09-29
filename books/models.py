from django.utils import timezone
from django.db import models
from taggit.managers import TaggableManager
from django.urls import reverse
from accounts.models import Profile, MyUser


class Books(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=20)
    author = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='books')
    description = models.TextField()
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tags = TaggableManager()
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT)
    pdf_file = models.FileField(upload_to='books/pdfs/', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('books:book_detail', args=[self.id])

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'


class Comments(models.Model):
    books = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='comments')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.profile.user.username}'


class Author(models.Model):
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    birth_date = models.DateField()
    about = models.TextField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('books:actor_detail',
                       args=[self.id])

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
