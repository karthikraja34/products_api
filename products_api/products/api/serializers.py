from rest_framework import serializers


class UploadSerializer(serializers.Serializer):
    uploaded_file = serializers.FileField(required=True)

    class Meta:
        fields = ["uploaded_file"]
