from django.contrib import admin
from .models import User, Profile
from books.models import Books

class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1  # Количество пустых форм для добавления профиля

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'date_joined', 'date_of_birth')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('date_joined',)
    inlines = [ProfileInline]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_purchased_books', 'get_bookmarks')
    search_fields = ('user__username', 'user__email')
    list_filter = ('user__date_joined',)

    def get_purchased_books(self, obj):
        return ", ".join([book.title for book in obj.purchased_books.all()])
    get_purchased_books.short_description = 'Purchased Books'

    def get_bookmarks(self, obj):
        return ", ".join([book.title for book in obj.bookmarks.all()])
    get_bookmarks.short_description = 'Bookmarks'

