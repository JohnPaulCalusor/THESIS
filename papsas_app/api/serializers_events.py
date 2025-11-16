from datetime import datetime, time

from django.utils import timezone
from rest_framework import serializers

from papsas_app.models import Event


class EventSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="eventName")
    summary = serializers.SerializerMethodField()
    body_html = serializers.SerializerMethodField()
    starts_at = serializers.SerializerMethodField()
    ends_at = serializers.SerializerMethodField()
    is_all_day = serializers.SerializerMethodField()
    location_text = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "summary",
            "body_html",
            "starts_at",
            "ends_at",
            "is_all_day",
            "location_text",
            "cover_image",
            "status",
            "slug",
            "created",
            "updated",
            "created_by",
        ]

    def _combine(self, date_value, time_value):
        if not date_value:
            return None
        combined = datetime.combine(date_value, time_value or time(0, 0))
        if timezone.is_naive(combined):
            combined = timezone.make_aware(combined, timezone.get_current_timezone())
        return combined

    def _format(self, value):
        if not value:
            return None
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.get_current_timezone())
        return value.isoformat()

    def _build_location(self, obj):
        if obj.venue:
            parts = [obj.venue.name or "", obj.venue.address or ""]
            return ", ".join(p for p in (part.strip() for part in parts) if p)
        return ""

    def _absolute_image(self, request, field):
        if not field:
            return None
        try:
            return request.build_absolute_uri(field.url)
        except Exception:
            return field.url

    def get_summary(self, obj):
        text = (obj.eventDescription or "").strip()
        if len(text) > 200:
            return f"{text[:200].rstrip()}..."
        return text

    def get_body_html(self, obj):
        return obj.eventDescription or ""

    def get_starts_at(self, obj):
        return self._format(self._combine(obj.startDate, obj.startTime))

    def get_ends_at(self, obj):
        return self._format(self._combine(obj.endDate or obj.startDate, obj.endTime))

    def get_is_all_day(self, obj):
        return obj.startTime is None and obj.endTime is None

    def get_location_text(self, obj):
        return self._build_location(obj)

    def get_cover_image(self, obj):
        request = self.context.get("request")
        primary = obj.cover_image or obj.pubmat
        return self._absolute_image(request, primary)

    def get_status(self, obj):
        return "published" if obj.eventStatus else "draft"

    def get_slug(self, obj):
        return obj.slug or ""

    def get_created(self, obj):
        return obj.postStamp.isoformat() if obj.postStamp else None

    def get_updated(self, obj):
        return obj.updated_at.isoformat() if obj.updated_at else None

    def get_created_by(self, obj):
        if not obj.created_by:
            return None
        return {
            "id": obj.created_by_id,
            "username": obj.created_by.username,
            "email": obj.created_by.email,
        }
