import codecs
import csv
import itertools
import random
from itertools import islice

from celery import Task
from celery_progress.backend import ProgressRecorder
from django.conf import settings

from config.celery_app import app
from products_api.products.api.utils import get_s3_client
from products_api.products.models import Product


class ImportProductsTask(Task):
    BATCH_SIZE = 1000

    def run(self, *args, **kwargs):
        progress_recorder = ProgressRecorder(self)
        path = kwargs.get("path")
        file_object = self.get_file(path)
        reader = csv.reader(file_object)
        next(reader)
        reader, reader_copy = itertools.tee(reader)
        products = (dict(name=row[0], sku=row[1], description=row[2]) for row in reader)
        total_products_count = len(list(reader_copy))
        processed_products_count = 0

        while True:
            sliced_products = list(islice(products, self.BATCH_SIZE))
            processed_products_count += len(sliced_products)
            progress_recorder.set_progress(
                processed_products_count, total_products_count
            )
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
                            active=random.choice([True, False]),
                        )
                    )

            if records_to_be_created:
                Product.objects.bulk_create(records_to_be_created)

            if records_to_be_updated:
                Product.objects.bulk_update(
                    records_to_be_updated, ["name", "description"]
                )

    def get_file(self, s3_path):
        s3_client = get_s3_client()
        obj = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_path)
        return codecs.getreader("utf-8")(obj["Body"])


ImportProductsTask = app.register_task(ImportProductsTask())
