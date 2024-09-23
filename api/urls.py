from rest_framework.routers import DefaultRouter
from accounts.views import ProfileViewSet
from books.views import BookViewSet
from subscriptions.views import SubscriptionPlanViewSet

router = DefaultRouter()
router.register(r'accounts', ProfileViewSet)
router.register(r'books', BookViewSet)
router.register(r'subscriptions', SubscriptionPlanViewSet)

urlpatterns = router.urls