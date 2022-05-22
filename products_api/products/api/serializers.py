from rest_framework import serializers

from products_api.products.models import Product


class UploadSerializer(serializers.Serializer):
    uploaded_file = serializers.FileField(required=True)

    class Meta:
        fields = ["uploaded_file"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["name", "description", "sku", "id", "active"]
        model = Product
