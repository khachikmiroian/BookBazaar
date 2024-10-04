from django.contrib import admin
from .models import Books, Author


@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'price']


@admin.register(Author)
class AuthorsAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'birth_date']
