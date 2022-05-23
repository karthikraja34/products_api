from rest_framework import serializers

from products_api.products.models import Product


class PresignedURLInputSerializer(serializers.Serializer):
    file_name = serializers.CharField(required=True)

    class Meta:
        fields = ["file_name"]


class UploadSerializer(serializers.Serializer):
    key = serializers.CharField(required=True)

    class Meta:
        fields = ["key"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["name", "description", "sku", "id", "active"]
        model = Product
