import csv
from itertools import islice

from celery import Task
from django.conf import settings

from config.celery_app import app
from products_api.products.models import Product


class ImportProductsTask(Task):
    BATCH_SIZE = 1000

    def run(self, *args, **kwargs):
        path = kwargs.get("path")
        with open(settings.MEDIA_ROOT + "/" + path) as file:
            reader = csv.reader(file)
            next(reader)
            products = (
                dict(name=row[0], sku=row[1], description=row[2]) for row in reader
            )

            while True:
                sliced_products = list(islice(products, self.BATCH_SIZE))
                if not sliced_products:
                    break

                sku_dict = {product["sku"]: product for product in sliced_products}
                sku_to_product_map = Product.objects.filter(
                    sku__in=sku_dict.keys()
                ).in_bulk(field_name="sku")
                records_to_be_created = []
                records_to_be_updated = []

                for sku, data in sku_dict.items():
                    if sku in sku_to_product_map:
                        existing_product = sku_to_product_map[sku]
                        existing_product.name = data["name"]
                        existing_product.description = data["description"]
                        records_to_be_updated.append(existing_product)
                    else:
                        records_to_be_created.append(
                            Product(
                                name=data["name"],
                                sku=data["sku"],
                                description=data["description"],
                            )
                        )

                if records_to_be_created:
                    Product.objects.bulk_create(records_to_be_created)

                if records_to_be_updated:
                    Product.objects.bulk_update(
                        records_to_be_updated, ["name", "description"]
                    )


ImportProductsTask = app.register_task(ImportProductsTask())
