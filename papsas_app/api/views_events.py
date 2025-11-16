from datetime import datetime, timedelta, time, timezone as dt_timezone

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from papsas_app.api.serializers_events import EventSerializer
from papsas_app.models import Event


def _combine_date_time(date_value, time_value):
    if not date_value:
        return None
    combined = datetime.combine(date_value, time_value or time(0, 0))
    if timezone.is_naive(combined):
        combined = timezone.make_aware(combined, timezone.get_current_timezone())
    return combined


def _format_datetime(value, all_day=False):
    if not value:
        return None
    aware = value
    if timezone.is_naive(aware):
        aware = timezone.make_aware(aware, timezone.get_default_timezone())
    if all_day:
        return aware.date().strftime("%Y%m%d")
    return aware.astimezone(dt_timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _calendar_lines(events):
    yield "BEGIN:VCALENDAR"
    yield "VERSION:2.0"
    yield f"PRODID:-//{settings.SITE_DOMAIN}//EN"
    for event in events:
        start = _combine_date_time(event.startDate, event.startTime)
        end = _combine_date_time(event.endDate or event.startDate, event.endTime)
        is_all_day = event.startTime is None and event.endTime is None
        yield "BEGIN:VEVENT"
        yield f"UID:event-{event.id}@{settings.SITE_DOMAIN}"
        yield f"DTSTAMP:{_format_datetime(timezone.now())}"
        if start:
            if is_all_day:
                yield f"DTSTART;VALUE=DATE:{_format_datetime(start, all_day=True)}"
            else:
                yield f"DTSTART:{_format_datetime(start)}"
        if end:
            if is_all_day:
                adjusted_end = end + timedelta(days=1)
                yield f"DTEND;VALUE=DATE:{_format_datetime(adjusted_end, all_day=True)}"
            else:
                yield f"DTEND:{_format_datetime(end)}"
        description = (event.eventDescription or "").replace("\r\n", "\n").replace("\n", "\\n")
        if description:
            yield f"DESCRIPTION:{description}"
        if event.venue:
            location = ", ".join(p for p in (event.venue.name, event.venue.address) if p)
            if location:
                yield f"LOCATION:{location}"
        yield f"SUMMARY:{event.eventName or 'Event'}"
        if event.slug:
            yield f"URL:https://{settings.SITE_DOMAIN}/event/{event.slug}"
        yield "END:VEVENT"
    yield "END:VCALENDAR"


@api_view(["GET"])
@permission_classes([AllowAny])
def events_list(request):
    qs = Event.objects.filter(eventStatus=True).order_by("-startDate")
    serializer = EventSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, eventStatus=True)
    serializer = EventSerializer(event, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def events_ics(request):
    events = Event.objects.filter(eventStatus=True).order_by("startDate")
    body = "\r\n".join(_calendar_lines(events)) + "\r\n"
    response = HttpResponse(body, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="events.ics"'
    return response
