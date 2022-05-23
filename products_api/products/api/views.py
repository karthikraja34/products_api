import os
import uuid

from django.conf import settings
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from products_api.products.api.filters import ProductFilter
from products_api.products.api.serializers import (
    PresignedURLInputSerializer,
    ProductSerializer,
    UploadSerializer,
)
from products_api.products.api.utils import get_s3_client
from products_api.products.models import Product
from products_api.products.tasks import ImportProductsTask


class AwsPreSignedUrlView(APIView):
    serializer_class = PresignedURLInputSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        file_name = serializer.validated_data["file_name"]
        key, url = self.generate_presigned_url(file_name)
        return Response(data={"key": key, "url": url}, status=200)

    def generate_presigned_url(self, file_name):
        s3 = get_s3_client()
        extension = os.path.splitext(file_name)[1]
        params = {
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": uuid.uuid4().hex + extension.lower(),
        }
        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params=params,
            ExpiresIn=3600,
        )
        return params["Key"], url


class UploadProductsView(APIView):
    serializer_class = UploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        task = ImportProductsTask.apply_async(
            kwargs={"path": serializer.validated_data["key"]}
        )
        return Response(
            data={
                "task_id": task.task_id,
                "progress_url": reverse(
                    "api:products:task_status", kwargs={"task_id": task.task_id}
                ),
            }
        )


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


@api_view(["DELETE"])
def delete_all(request):
    Product.objects.truncate()
    return Response("All products are deleted", status=status.HTTP_200_OK)
