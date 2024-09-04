from django.db import models
from taggit.managers import TaggableManager
from django.urls import reverse


class Books(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=20)
    author = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='author')
    description = models.TextField()
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tags = TaggableManager()

    def __str__(self):
        return self.title


class Author(models.Model):
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    birth_date = models.DateField()
    about = models.TextField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

