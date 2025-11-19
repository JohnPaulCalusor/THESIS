from django.db import connection
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple DRF health check.

    - Verifies DB connectivity via `SELECT 1`.
    - Returns a small JSON payload that is safe for load balancers / uptime robots.

    Response shape:
    {
        "status": "ok" | "error",
        "db": "ok" | "error: <detail>",
        "time": "<ISO-8601 timestamp>"
    }
    """
    db_status = "ok"

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:  # pragma: no cover (rare in normal ops)
        db_status = f"error: {exc.__class__.__name__}"

    overall_status = "ok" if db_status == "ok" else "error"

    return Response(
        {
            "status": overall_status,
            "db": db_status,
            "time": timezone.now().isoformat(),
        }
    )
