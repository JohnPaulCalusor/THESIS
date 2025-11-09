# >>> PAPSAS v1.4 BEGIN
from rest_framework.throttling import SimpleRateThrottle


class ExplainPerUserElectionThrottle(SimpleRateThrottle):
    scope = 'explain'

    def get_cache_key(self, request, view):
        try:
            election_id = int(view.kwargs.get('election_id') or view.kwargs.get('id') or 0)
        except Exception:
            election_id = 0
        user_id = getattr(getattr(request, 'user', None), 'id', None)
        if not user_id or not election_id:
            return None
        ident = f"{user_id}:{election_id}"
        return self.cache_key(ident)

    def cache_key(self, ident: str) -> str:
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident,
        }
# <<< PAPSAS v1.4 END

