from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import ProductViewSet

urlpatterns = [
    path("bulk_upload/", views.UploadProductsView.as_view(), name="index"),
    path("delete_all/", views.delete_all, name="delete_all"),
]

router = DefaultRouter()
router.register(r"", ProductViewSet, basename="")
urlpatterns += router.urls
