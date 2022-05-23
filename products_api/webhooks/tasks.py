import json

import requests
from celery import Task
from django.core.serializers.json import DjangoJSONEncoder

from config.celery_app import app


class SendWebhookTask(Task):
    def run(self, target, payload, *args, **kwargs):
        try:
            response = requests.post(
                url=target,
                data=json.dumps(payload, cls=DjangoJSONEncoder),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except (requests.ConnectionError, requests.HTTPError):
            delay_in_seconds = 2**self.request.retries
            self.retry(countdown=delay_in_seconds)


SendWebhookTask = app.register_task(SendWebhookTask())
