from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from products_api.products.api.filters import ProductFilter
from products_api.products.api.serializers import ProductSerializer, UploadSerializer
from products_api.products.models import Product
from products_api.products.tasks import ImportProductsTask


class UploadProductsView(APIView):
    serializer_class = UploadSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        path = default_storage.save(
            settings.MEDIA_ROOT + "/products.csv",
            ContentFile(serializer.validated_data["uploaded_file"].read()),
        )
        ImportProductsTask.apply_async(kwargs={"path": path})
        return Response("Products are being uploaded.")


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
