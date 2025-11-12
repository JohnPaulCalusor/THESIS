from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserSecurity
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_user_security(sender, instance, created, **kwargs):
    if created:
        UserSecurity.objects.create(user=instance)
