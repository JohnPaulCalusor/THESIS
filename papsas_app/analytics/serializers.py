from rest_framework import serializers

from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "ts",
            "actor_username",
            "action",
            "status",
            "scope_election_id",
            "target_type",
            "target_id",
            "ip",
            "user_agent",
            "method",
            "path",
            "payload_hash",
            "meta",
        )
