from rest_framework import serializers
from .models import SubscriptionPlan  # Предположим, что ваша модель называется Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'