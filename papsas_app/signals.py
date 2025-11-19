import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from exponent_server_sdk import (
    PushClient,
    PushMessage,
    DeviceNotRegisteredError,
    PushServerError,
)
from django.contrib.auth import get_user_model

from .models import DevicePushToken, Event, UserSecurity

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def ensure_user_security(sender, instance, created, **kwargs):
    if created:
        UserSecurity.objects.create(user=instance)


@receiver(post_save, sender=Event)
def send_push_on_new_published_event(sender, instance: Event, created: bool, **kwargs):
    """
    When a new Event is created and published, notify all active devices.
    """
    try:
        if not created:
            return
        if not getattr(instance, "eventStatus", False):
            return
    except Exception:
        logger.exception("Error evaluating Event conditions for push notification.")
        return

    tokens = list(DevicePushToken.objects.filter(is_active=True).values_list("token", flat=True))

    if not tokens:
        logger.info("No active DevicePushToken records; skipping push broadcast.")
        return

    client = PushClient()
    title = "New event posted"
    body = getattr(instance, "eventName", "New event")
    event_id = instance.pk

    for token in tokens:
        message = PushMessage(
            to=token,
            title=title,
            body=body,
            data={"eventId": event_id},
        )
        try:
            client.publish(message)
        except DeviceNotRegisteredError:
            DevicePushToken.objects.filter(token=token).update(is_active=False)
            logger.info("Deactivated DevicePushToken for unregistered device: %s", token)
        except PushServerError as exc:
            logger.warning("PushServerError when sending push to %s: %s", token, exc)
        except Exception:
            logger.exception("Unexpected error while sending push notification.")
