from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from model_utils.models import TimeStampedModel

from products_api.webhooks.tasks import SendWebhookTask


class Webhook(TimeStampedModel):
    event = models.CharField("Event", max_length=64, db_index=True)
    target = models.URLField("Target URL", max_length=255)

    def clean(self):
        if self.event not in settings.HOOK_EVENTS.keys():
            raise ValidationError(f"Invalid hook event {self.event}.")

    def dict(self):
        return {"event": self.event, "target": self.target}

    def serialize_hook(self, instance):
        if getattr(instance, "serialize_hook", None) and callable(
            instance.serialize_hook
        ):
            return instance.serialize_hook(hook=self)
        return {}

    def send_hook(self, instance):
        payload = self.serialize_hook(instance)
        SendWebhookTask.apply_async(args=(self.target, payload))


def get_model_label(instance):
    if instance is None:
        return None
    opts = instance._meta.concrete_model._meta
    try:
        return opts.label
    except AttributeError:
        return ".".join([opts.app_label, opts.object_name])


@receiver(post_save, dispatch_uid="instance-saved-hook")
def on_model_save(sender, instance, created, *args, **kwargs):
    from products_api.webhooks.utils import send_webhook

    model_label = get_model_label(instance)
    action = "created" if created else "updated"
    send_webhook(instance, model_label, action)
