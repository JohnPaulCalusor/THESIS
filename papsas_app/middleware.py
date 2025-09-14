# middleware.py
from .models import VisitorStats

class VisitorCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_key = 'has_visited'
        if not request.session.get(session_key, False):
            visitor_stat, _ = VisitorStats.objects.get_or_create(id=1)
            visitor_stat.total_visitors += 1
            visitor_stat.save()
            request.session[session_key] = True  # Mark user as counted

        return self.get_response(request)
