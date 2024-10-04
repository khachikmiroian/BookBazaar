from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from subscriptions.models import Subscription


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)


class MyUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)
    purchased_books = models.ManyToManyField('books.Books', related_name='purchasers', blank=True)
    
    def __str__(self):
        return f'Profile of {self.user.username}'

    def get_active_subscription(self):
        return Subscription.objects.filter(user=self.user, end_date__gt=timezone.now()).first()


