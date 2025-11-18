from django.db import DatabaseError, connections

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """
    Light-weight health check for automated probes.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Returns {"status": "ok"} when the default DB connection can be established.
        If the DB check fails, responds with a 500 and {"status": "error", "code": "DB_UNAVAILABLE", ...}.
        """
        try:
            connections["default"].ensure_connection()
        except DatabaseError as exc:
            return Response(
                {"status": "error", "code": "DB_UNAVAILABLE", "message": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
