from celery_progress.views import get_progress
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import ProductViewSet

urlpatterns = [
    path("bulk_upload/", views.UploadProductsView.as_view(), name="index"),
    path("pre_signed_url/", views.AwsPreSignedUrlView.as_view(), name="pre_signed_url"),
    path("delete_all/", views.delete_all, name="delete_all"),
    path("bulk_upload_progress/<str:task_id>", get_progress, name="task_status"),
]

router = DefaultRouter()
router.register(r"", ProductViewSet, basename="")
urlpatterns += router.urls
