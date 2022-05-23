from rest_framework import serializers

from products_api.webhooks.models import Webhook


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["event", "target", "id"]
        model = Webhook
