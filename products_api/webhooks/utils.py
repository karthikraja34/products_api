from django.conf import settings

from products_api.webhooks.models import Webhook


def get_event_config():
    config = {}
    for event_name, model_config in settings.WEBHOOK_EVENTS.items():
        model_label, action = model_config.rsplit(".", 1)
        cc = config.setdefault(model_label, {})
        cc[action] = event_name
    return config


def send_webhook(instance, model_label, action):
    event_config = get_event_config()
    event_name = event_config.get(model_label, {}).get(action, None)
    if event_name:
        webhooks = Webhook.objects.filter(event=event_name)
        for webhook in webhooks:
            webhook.send_hook(instance)
