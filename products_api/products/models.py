from django.db import connection, models
from model_utils.models import TimeStampedModel


class ProductManager(models.Manager):
    def truncate(self):
        with connection.cursor() as cursor:
            cursor.execute(f'TRUNCATE TABLE "{self.model._meta.db_table}" CASCADE')


class Product(TimeStampedModel):
    name = models.CharField("Product name", max_length=255)
    sku = models.CharField("SKU", max_length=300, unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField("Active")

    def serialize_hook(self, hook):
        return {
            "meta": hook.dict(),
            "data": {
                "name": self.name,
                "sku": self.sku,
                "description": self.description,
                "active": self.active,
            },
        }
