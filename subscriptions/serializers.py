from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, BookPurchase
from books.models import Books
from accounts.serializers import UserSerializer


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price']


class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'start_date', 'end_date', 'is_active']
        read_only_fields = ['id', 'user', 'plan', 'start_date', 'end_date', 'is_active']


class BookPurchaseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Books.objects.all())

    class Meta:
        model = BookPurchase
        fields = ['id', 'user', 'book', 'purchase_date']
        read_only_fields = ['id', 'user', 'purchase_date']
