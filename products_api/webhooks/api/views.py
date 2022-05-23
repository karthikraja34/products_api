from rest_framework import viewsets

from products_api.webhooks.api.serializers import WebhookSerializer
from products_api.webhooks.models import Webhook


class WebhookViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookSerializer
    queryset = Webhook.objects.all()
