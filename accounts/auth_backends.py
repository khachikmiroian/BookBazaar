from django.contrib.auth.backends import BaseBackend
from .models import MyUser  # Убедитесь, что это ваша модель пользователя


class EmailAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = MyUser.objects.get(username=username)
            if user.check_password(password):
                return user
        except MyUser.DoesNotExist:
            user = None
        try:
            user = MyUser.objects.get(email=username)
            if user.check_password(password):
                return user
        except MyUser.DoesNotExist:
            return None

        return None

    def get_user(self, user_id):
        try:
            return MyUser.objects.get(pk=user_id)
        except MyUser.DoesNotExist:
            return None
