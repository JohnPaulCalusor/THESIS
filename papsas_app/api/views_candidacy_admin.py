from django.apps import apps
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

Election  = apps.get_model("papsas_app", "Election")
Candidacy = apps.get_model("papsas_app", "Candidacy")
Position  = apps.get_model("papsas_app", "Position")
User      = apps.get_model("papsas_app", "User")

def display_name(u: User | None) -> str:
    if not u:
        return ""
    first = getattr(u, "first_name", "") or ""
    last  = getattr(u, "last_name", "") or ""
    pretty = (first + " " + last).strip()
    return pretty or getattr(u, "email", "") or getattr(u, "username", "") or f"User#{getattr(u, 'pk', '0')}"

class CandidacyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, election_id: int):
        try:
            Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({"detail": "Election not found."}, status=404)

        qs = (
            Candidacy.objects
            .select_related("candidate", "position")
            .filter(election_id=election_id)
            .order_by("id")
        )

        rows = []
        for c in qs:
            u = getattr(c, "candidate", None)
            rows.append({
                "id": c.id,
                "candidacyStatus": getattr(c, "candidacyStatus", True),
                "credentials": getattr(c, "credentials", None),
                "candidate": {
                    "id": getattr(u, "id", None),
                    "name": display_name(u) or getattr(c, "name", None),
                    "email": getattr(u, "email", None),
                    "username": getattr(u, "username", None),
                },
                "position": ({
                    "id": c.position_id,
                    "title": getattr(c.position, "title", None),
                } if getattr(c, "position_id", None) else None),
            })

        return Response({"results": rows}, status=200)
