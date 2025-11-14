from django.apps import apps
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

Election  = apps.get_model("papsas_app", "Election")
Position  = apps.get_model("papsas_app", "Position")
Candidacy = apps.get_model("papsas_app", "Candidacy")
User      = apps.get_model("papsas_app", "User")

def display_name(u: User | None) -> str:
    if not u:
        return ""
    first = getattr(u, "first_name", "") or ""
    last  = getattr(u, "last_name", "") or ""
    pretty = (first + " " + last).strip()
    return pretty or getattr(u, "email", "") or getattr(u, "username", "") or f"User#{getattr(u, 'pk', '0')}"

class ElectionBallotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, election_id: int):
        # ensure election exists
        try:
            e = Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({"detail": "Election not found."}, status=404)

        # load positions (ordered) and candidacies
        pos_qs = Position.objects.filter(election_id=election_id).order_by("sort", "id")
        cands  = (
            Candidacy.objects
            .select_related("position", "candidate")
            .filter(election_id=election_id, candidacyStatus=True)
        )

        # group choices per position
        by_pos: dict[int, list[dict]] = {}
        at_large: list[dict] = []
        for c in cands:
            u = getattr(c, "candidate", None)
            name = display_name(u) or getattr(c, "name", f"Candidacy#{c.id}")

            # include both camelCase and snake_case keys to be frontend-friendly
            item = {
                "candidacyId": c.id,
                "candidacy_id": c.id,
                "candidateId": getattr(u, "id", None),
                "candidate_id": getattr(u, "id", None),
                "name": name,
            }

            if getattr(c, "position_id", None):
                by_pos.setdefault(c.position_id, []).append(item)
            else:
                at_large.append(item)

        positions = []
        for p in pos_qs:
            positions.append({
                "id": p.id,
                "title": p.title,
                "winners": getattr(p, "winners", None),
                # web expects options/choices; include both for compatibility
                "options": by_pos.get(p.id, []),
                "choices": by_pos.get(p.id, []),
            })

        # payload; positions-first; keep atLarge as fallback for legacy UI
        return Response({
            "election": {
                "id": e.id,
                "title": getattr(e, "title", None),
                "numWinners": getattr(e, "numWinners", None),
            },
            "positions": positions,
            "atLarge": at_large,  # safe extra; frontend can ignore
        }, status=200)
