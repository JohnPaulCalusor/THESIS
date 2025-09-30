# middleware.py
from django.db import DatabaseError

from .models import VisitorStats

class VisitorCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip visitor counting for health checks so the endpoint stays DB-free
        if request.path == "/api/health":
            return self.get_response(request)

        session_key = 'has_visited'
        if not request.session.get(session_key, False):
            try:
                visitor_stat, _ = VisitorStats.objects.get_or_create(id=1)
                visitor_stat.total_visitors += 1
                visitor_stat.save(update_fields=["total_visitors"])
            except DatabaseError:
                # If the database is unavailable, fail open so requests still work
                return self.get_response(request)
            request.session[session_key] = True  # Mark user as counted

        return self.get_response(request)
