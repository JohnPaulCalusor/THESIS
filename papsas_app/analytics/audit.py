import hashlib
import json

from django.conf import settings
from django.db import transaction

from .models import AuditEvent

SENSITIVE_KEYS = {"password", "refresh", "access", "otp", "token"}


def scrub_payload(obj):
    """Return a copy of obj where sensitive keys are masked."""
    if isinstance(obj, dict):
        cleaned = {}
        for key, value in obj.items():
            normalized = key.lower()
            if normalized in SENSITIVE_KEYS:
                cleaned[key] = "***"
            else:
                cleaned[key] = scrub_payload(value)
        return cleaned
    if isinstance(obj, (list, tuple)):
        return type(obj)(scrub_payload(item) for item in obj)
    return obj


def _safe_hash(payload):
    """Return a deterministic sha256 hash of the scrubbed payload."""
    if not payload:
        return ""
    scrubbed = scrub_payload(payload)
    raw = json.dumps(scrubbed, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def log_event(
    request,
    *,
    action,
    status="success",
    target_type="",
    target_id="",
    scope_election_id=None,
    meta=None,
    payload_for_hash=None,
):
    if not getattr(settings, "AUDIT_ENABLED", True):
        return

    user = getattr(request, "user", None)
    actor = user if getattr(user, "is_authenticated", False) else None
    actor_username = getattr(user, "username", "") if actor else ""

    client_ip = getattr(request, "client_ip", None) or request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    method = request.method or ""
    path = request.get_full_path()
    payload_hash = _safe_hash(payload_for_hash or {})
    meta = meta or {}

    def _create():
        AuditEvent.objects.create(
            actor=actor,
            actor_username=actor_username,
            action=action,
            scope_election_id=scope_election_id,
            target_type=target_type,
            target_id=target_id,
            status=status,
            ip=client_ip,
            user_agent=user_agent,
            method=method,
            path=path,
            payload_hash=payload_hash,
            meta=meta,
        )

    transaction.on_commit(_create)
