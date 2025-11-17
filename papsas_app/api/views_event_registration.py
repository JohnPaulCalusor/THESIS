from typing import Optional

from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from papsas_app.analytics.models import AuditEvent
from papsas_app.models import Event, EventSignup

from .api_errors import error_response


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
            return error_response("NOT_FOUND", "Event not found.")
        registered = EventSignup.objects.filter(event=event, user=request.user).exists()
        return Response({"registered": registered}, status=status.HTTP_200_OK)

    def post(self, request, event_id: int):
        event = self._resolve_event(event_id)
        if not event:
            return error_response("NOT_FOUND", "Event not found.")
        _, created = EventSignup.objects.get_or_create(event=event, user=request.user)
        if not created:
            self._record_rejected(reason="already_registered")
            return error_response(
                "ALREADY_REGISTERED",
                "You are already registered for this event.",
            )
        self._record_success("REGISTRATION_CREATED")
        return Response({"registered": True}, status=status.HTTP_201_CREATED)

    def delete(self, request, event_id: int):
        event = self._resolve_event(event_id)
        if not event:
            return error_response("NOT_FOUND", "Event not found.")
        registration = EventSignup.objects.filter(event=event, user=request.user)
        if not registration.exists():
            self._record_rejected(reason="not_registered")
            return error_response(
                "NOT_REGISTERED",
                "You are not registered for this event.",
            )
        registration.delete()
        self._record_success("REGISTRATION_DELETED")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_exception(self, exc):
        if isinstance(exc, Throttled):
            self._record_rejected(reason="throttled")
        return super().handle_exception(exc)

    def _resolve_event(self, event_id: int):
        try:
            return Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            self._record_rejected(reason="event_not_found")
            return None

    def _record_success(self, action: str):
        event_id = self._effective_event_id()
        user_id = self._user_id()
        if event_id is None or user_id is None:
            return
        self._record_event(action, "success", event_id, user_id)

    def _record_rejected(self, reason: str):
        event_id = self._effective_event_id()
        user_id = self._user_id()
        if event_id is None or user_id is None:
            return
        self._record_event("REGISTRATION_REJECTED", "error", event_id, user_id, reason=reason)

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
        event_id: Optional[int],
        user_id: Optional[int],
        *,
        reason: Optional[str] = None,
    ):
        if self.request is None or event_id is None or user_id is None:
            return
        target_id = str(event_id)
        meta = {"event_id": event_id, "user_id": user_id}
        if reason:
            meta["reason"] = reason
        request = self.request
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
