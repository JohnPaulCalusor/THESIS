from typing import Optional

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from papsas_app.analytics.models import AuditEvent
from papsas_app.models import Event, EventSignup

from .api_errors import (
    EVENT_CLOSED,
    EVENT_NOT_FOUND,
    MEMBER_ONLY,
    error_response,
)


class EventRegistrationView(APIView):
    """
    Manages registration state for the authenticated user and the requested event.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "event_register"

    def get_throttles(self):
        if self.request.method == "GET":
            return []
        return super().get_throttles()

    def get(self, request, event_id: int):
        event = self._resolve_event(event_id)
        if not event:
            return error_response(EVENT_NOT_FOUND)
        registered = EventSignup.objects.filter(event=event, user=request.user).exists()
        return Response({"registered": registered}, status=status.HTTP_200_OK)

    def post(self, request, event_id: int):
        event = self._resolve_event(event_id)
        if not event:
            return error_response(EVENT_NOT_FOUND)
        if not self._is_member(request.user):
            self._record_rejected(reason="non_member", event=event, request=request)
            return error_response(MEMBER_ONLY)
        rejection = self._ensure_event_open_for_registration(event, request=request)
        if rejection:
            return rejection
        try:
            with transaction.atomic():
                _, created = EventSignup.objects.get_or_create(event=event, user=request.user)
        except IntegrityError:
            self._record_rejected(reason="already_registered", event=event, request=request)
            return error_response(
                "ALREADY_REGISTERED",
                "You are already registered for this event.",
            )
        if not created:
            self._record_rejected(reason="already_registered", event=event, request=request)
            return error_response(
                "ALREADY_REGISTERED",
                "You are already registered for this event.",
            )
        self._record_success("REGISTRATION_CREATED", event=event, request=request)
        return Response({"registered": True}, status=status.HTTP_201_CREATED)

    def delete(self, request, event_id: int):
        event = self._resolve_event(event_id)
        if not event:
            return error_response(EVENT_NOT_FOUND)
        if not self._is_member(request.user):
            self._record_rejected(reason="non_member", event=event, request=request)
            return error_response(MEMBER_ONLY)
        registration = EventSignup.objects.filter(event=event, user=request.user)
        if not registration.exists():
            self._record_rejected(reason="not_registered", event=event, request=request)
            return error_response(
                "NOT_REGISTERED",
                "You are not registered for this event.",
            )
        registration.delete()
        self._record_success("REGISTRATION_DELETED", event=event, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_exception(self, exc):
        if isinstance(exc, Throttled):
            self._record_rejected(reason="throttled", request=self.request)
        return super().handle_exception(exc)

    def _resolve_event(self, event_id: int):
        try:
            return Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            self._record_rejected(reason="event_not_found")
            return None

    def _is_member(self, user) -> bool:
        if not user or not getattr(user, "is_authenticated", False):
            return False
        today = timezone.localdate()
        member_manager = getattr(user, "member", None)
        if member_manager is not None:
            if member_manager.filter(expirationDate__gt=today, status="Approved").exists():
                return True
        groups = getattr(user, "groups", None)
        if groups is not None:
            return groups.filter(name="member").exists()
        return False

    def _ensure_event_open_for_registration(self, event, *, request=None):
        if not getattr(event, "eventStatus", True):
            self._record_rejected(reason="unpublished", event=event, request=request)
            return error_response(EVENT_NOT_FOUND)
        today = timezone.localdate()
        end_date = getattr(event, "endDate", None)
        if end_date and end_date < today:
            self._record_rejected(reason="closed", event=event, request=request)
            return error_response(EVENT_CLOSED)
        return None

    def _record_success(self, action: str, *, event=None, request=None):
        self._record_event(action, "success", event=event, request=request)

    def _record_rejected(self, reason: str, *, event=None, request=None):
        self._record_event("REGISTRATION_REJECTED", "error", event=event, request=request, reason=reason)

    def _effective_event_id(self) -> Optional[int]:
        kwargs = getattr(self, "kwargs", {})
        value = kwargs.get("event_id")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    def _user_id(self) -> Optional[int]:
        user = getattr(self.request, "user", None)
        return getattr(user, "id", None) if user else None

    def _record_event(
        self,
        action: str,
        status_label: str,
        *,
        event=None,
        request=None,
        reason: Optional[str] = None,
    ):
        request_obj = request or getattr(self, "request", None)
        if request_obj is None:
            return
        event_id = getattr(event, "id", None) if event else self._effective_event_id()
        user = getattr(request_obj, "user", None)
        user_id = getattr(user, "id", None) if user else None
        if event_id is None or user_id is None:
            return
        target_id = str(event_id)
        meta = {"event_id": event_id, "user_id": user_id}
        if reason:
            meta["reason"] = reason
        request = request_obj
        actor = None
        user = getattr(request, "user", None)
        if getattr(user, "is_authenticated", False):
            actor = user
        actor_username = getattr(user, "username", "") if actor else ""
        ip = getattr(request, "client_ip", None) or request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        method = request.method or ""
        path = request.get_full_path()
        AuditEvent.objects.create(
            actor=actor,
            actor_username=actor_username,
            action=action,
            target_type="event",
            target_id=target_id,
            status=status_label,
            ip=ip,
            user_agent=user_agent,
            method=method,
            path=path,
            meta=meta,
        )
