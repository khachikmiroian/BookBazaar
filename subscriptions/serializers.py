from rest_framework import serializers
from .models import SubscriptionPlan

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'