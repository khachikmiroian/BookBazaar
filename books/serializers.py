from rest_framework import serializers
from .models import Books, Author, Comments, Bookmarks
from subscriptions.models import Subscription, BookPurchase
from accounts.serializers import ProfileSerializer


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'birth_date', 'about']
        read_only_fields = ['id', 'first_name', 'last_name', 'birth_date', 'about']


class CommentsSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Comments
        fields = ['id', 'books', 'profile', 'content', 'created_at', 'updated_at', 'is_modified']
        read_only_fields = ['id', 'profile', 'created_at', 'updated_at', 'is_modified']


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='slug'
    )
    comments = CommentsSerializer(many=True, read_only=True)
    can_view_pdf = serializers.SerializerMethodField()

    class Meta:
        model = Books
        fields = ['id', 'title', 'author', 'description', 'date', 'price', 'tags', 'status', 'pdf_file', 'comments',
                  'can_view_pdf']
        read_only_fields = ['id', 'title', 'author', 'description', 'date', 'price', 'tags', 'status', 'pdf_file',
                            'comments', 'can_view_pdf']

    def get_can_view_pdf(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        user = request.user

        try:
            subscription = user.subscription
            if subscription.is_active:
                return True
        except Subscription.DoesNotExist:
            pass

        return BookPurchase.objects.filter(user=user, book=obj).exists()


class BookmarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmarks
        fields = ['id', 'profile', 'book', 'date_added']
        read_only_fields = ['id', 'profile', 'date_added']
