from rest_framework import serializers
from .models import Profile  # Предположим, что ваша модель для аккаунтов называется UserAccount

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'