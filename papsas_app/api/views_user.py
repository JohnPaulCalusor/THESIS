from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Q


User = get_user_model()


class UserSearchView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        term = (request.query_params.get("search") or "").strip()
        if not term:
            return Response({"results": []})
        qs = User.objects.filter(
            Q(email__icontains=term)
            | Q(username__icontains=term)
            | Q(first_name__icontains=term)
            | Q(last_name__icontains=term)
        )[:20]
        results = []
        for u in qs:
            results.append({
                "id": getattr(u, "id", None),
                "email": getattr(u, "email", None),
                "username": getattr(u, "username", None),
                "name": (getattr(u, "get_full_name", lambda: None)() or f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip()),
            })
        return Response({"results": results})
