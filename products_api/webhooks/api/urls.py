from rest_framework.routers import DefaultRouter

from .views import WebhookViewSet

router = DefaultRouter()
router.register(r"", WebhookViewSet, basename="")
urlpatterns = router.urls
