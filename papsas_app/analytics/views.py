import csv
import json

from datetime import datetime, timezone as dt_timezone

from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from papsas_app.analytics.models import AuditEvent
from papsas_app.analytics.serializers import AuditEventSerializer
from papsas_app.api.permissions import IsAdminOnly


def _parse_date(value):
    if not value:
        return None
    parsed = parse_datetime(value)
    if parsed is None:
        parsed_date = parse_date(value)
        if parsed_date is None:
            return None
        parsed = datetime(parsed_date.year, parsed_date.month, parsed_date.day)
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, dt_timezone.utc)
    else:
        parsed = parsed.astimezone(dt_timezone.utc)
    return parsed


def _filter_events(request):
    qs = AuditEvent.objects.all()
    actor = request.query_params.get("actor")
    if actor:
        qs = qs.filter(actor_username__iexact=actor)
    action = request.query_params.get("action")
    if action:
        qs = qs.filter(action=action)
    status = request.query_params.get("status")
    if status:
        qs = qs.filter(status=status)
    election = request.query_params.get("election") or request.query_params.get("scope_election_id")
    if election:
        try:
            election_id = int(election)
            qs = qs.filter(scope_election_id=election_id)
        except ValueError:
            pass
    q = request.query_params.get("q")
    if q:
        qs = qs.filter(Q(action__icontains=q) | Q(actor_username__icontains=q))
    since = _parse_date(request.query_params.get("since"))
    if since:
        qs = qs.filter(ts__gte=since)
    until = _parse_date(request.query_params.get("until"))
    if until:
        qs = qs.filter(ts__lte=until)
    return qs.order_by("-ts")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminOnly])
def audit_events(request):
    qs = _filter_events(request)
    total = qs.count()
    try:
        page = int(request.query_params.get("page", "1"))
    except ValueError:
        page = 1
    try:
        page_size = int(request.query_params.get("page_size", "50"))
    except ValueError:
        page_size = 50
    page = max(1, page)
    page_size = max(1, min(500, page_size))
    offset = (page - 1) * page_size
    objs = qs[offset: offset + page_size]
    serializer = AuditEventSerializer(objs, many=True)
    return Response(
        {
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": serializer.data,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminOnly])
def audit_export_csv(request):
    qs = _filter_events(request)[:50000]
    now = timezone.now().strftime("%Y%m%d%H%M%S")
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="audit-events-{now}.csv"'
    writer = csv.writer(resp, lineterminator="\n")
    writer.writerow(
        [
            "id",
            "ts",
            "actor_username",
            "action",
            "status",
            "scope_election_id",
            "target_type",
            "target_id",
            "ip",
            "method",
            "path",
            "payload_hash",
            "meta_json",
        ]
    )
    for ev in qs:
        writer.writerow(
            [
                ev.id,
                ev.ts.isoformat(),
                ev.actor_username,
                ev.action,
                ev.status,
                ev.scope_election_id,
                ev.target_type,
                ev.target_id,
                ev.ip,
                ev.method,
                ev.path,
                ev.payload_hash,
                json.dumps(ev.meta, separators=(",", ":")),
            ]
        )
    return resp
