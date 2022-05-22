from django.db import models
from model_utils.models import TimeStampedModel


class Product(TimeStampedModel):
    name = models.CharField("Product name", max_length=255)
    sku = models.CharField("SKU", max_length=300, unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField("Active")
