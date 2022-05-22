from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from products_api.products.api.serializers import UploadSerializer
from products_api.products.tasks import ImportProductsTask


def upload_products(request):
    return HttpResponse("Hello World")


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
        return Response("Uploaded successfuoly")
