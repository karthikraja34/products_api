from django.urls import path

from . import views

urlpatterns = [
    path("bulk_upload/", views.UploadProductsView.as_view(), name="index"),
]
