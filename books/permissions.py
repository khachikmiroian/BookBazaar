from rest_framework import permissions
from subscriptions.models import BookPurchase, Subscription


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.profile.user == request.user


class IsSubscribedOrPurchased(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        try:
            subscription = user.subscription
            if subscription.is_active:
                return True
        except Subscription.DoesNotExist:
            pass

        return BookPurchase.objects.filter(user=user, book=obj).exists()
