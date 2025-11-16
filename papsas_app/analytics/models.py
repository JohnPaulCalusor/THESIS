from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    """Persistent audit log records that can be expanded later."""

    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    actor_username = models.CharField(max_length=150, blank=True)

    action = models.CharField(max_length=64)
    scope_election_id = models.IntegerField(null=True, blank=True)
    target_type = models.CharField(max_length=64, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=16, default="success")

    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    method = models.CharField(max_length=8, blank=True)
    path = models.CharField(max_length=256, blank=True)

    payload_hash = models.CharField(max_length=64, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["action", "ts"]),
            models.Index(fields=["scope_election_id", "ts"]),
            models.Index(fields=["actor", "ts"]),
        ]
        ordering = ["-ts"]
