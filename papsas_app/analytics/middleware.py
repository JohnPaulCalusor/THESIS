from __future__ import annotations


class ClientIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.META.get("REMOTE_ADDR")
        request.client_ip = client_ip or None
        return self.get_response(request)
