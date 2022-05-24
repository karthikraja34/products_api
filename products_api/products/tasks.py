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
        self.progress_recorder = ProgressRecorder(self)
        path = kwargs.get("path")
        file_object = self.get_file_object(path)
        products, total_products_count = self.parse_csv(file_object)
        processed_products_count = 0

        while True:
            products_subset = list(islice(products, self.BATCH_SIZE))
            processed_products_count += len(products_subset)
            self.update_progress(processed_products_count, total_products_count)

            if not products_subset:
                break

            records_to_be_created, records_to_be_updated = self.get_records(
                products_subset
            )

            if records_to_be_created:
                Product.objects.bulk_create(records_to_be_created)

            if records_to_be_updated:
                Product.objects.bulk_update(
                    records_to_be_updated, ["name", "description"]
                )

    def get_records(self, products):
        sku_dict = {product["sku"]: product for product in products}
        existing_sku_to_product_map = Product.objects.filter(
            sku__in=sku_dict.keys()
        ).in_bulk(field_name="sku")

        records_to_be_created = []
        records_to_be_updated = []

        for sku, data in sku_dict.items():
            if sku in existing_sku_to_product_map:
                existing_product = existing_sku_to_product_map[sku]
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
        return records_to_be_created, records_to_be_updated

    def update_progress(self, processed_products_count, total_products_count):
        self.progress_recorder.set_progress(
            processed_products_count, total_products_count
        )

    def parse_csv(self, file_object):
        csv_reader = csv.reader(file_object)
        next(csv_reader)  # Skip first row as it is header
        csv_reader, reader_copy = itertools.tee(csv_reader)
        products = (
            dict(name=row[0], sku=row[1], description=row[2]) for row in csv_reader
        )
        total_products_count = len(list(reader_copy))
        return products, total_products_count

    def get_file_object(self, s3_path):
        s3_client = get_s3_client()
        obj = s3_client.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_path)
        return codecs.getreader("utf-8")(obj["Body"])


ImportProductsTask = app.register_task(ImportProductsTask())
