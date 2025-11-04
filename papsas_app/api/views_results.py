from collections import defaultdict
from django.apps import apps
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


User = apps.get_model("papsas_app", "User")
Election = apps.get_model("papsas_app", "Election")
Candidacy = apps.get_model("papsas_app", "Candidacy")
Position = apps.get_model("papsas_app", "Position")
VoteSelection = apps.get_model("papsas_app", "VoteSelection")


def display_name(u):
    parts = [getattr(u, "first_name", "") or "", getattr(u, "last_name", "") or ""]
    pretty = " ".join(p for p in parts if p).strip()
    return pretty or getattr(u, "email", "") or getattr(u, "username", "") or f"User#{getattr(u, 'pk', '0')}"


class ElectionResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, election_id: int):
        # Verify election exists
        try:
            election = Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({"detail": "Election not found."}, status=404)

        # Tally votes by candidacy_id
        tallies = {
            row["candidacy_id"]: row["count"]
            for row in VoteSelection.objects
                .filter(candidacy__election_id=election_id)
                .values("candidacy_id")
                .annotate(count=Count("id"))
        }

        # Load candidacies (+ related candidate + position if available)
        cands = (
            Candidacy.objects
            .select_related("candidate", "position")
            .filter(election_id=election_id)
        )

        # Group results
        by_pos = defaultdict(list)
        flat_results = []

        for c in cands:
            cnt = tallies.get(c.id, 0)
            u = getattr(c, "candidate", None)
            name = display_name(u) if u else getattr(c, "name", f"Candidacy#{c.id}")
            row = {
                "candidacy_id": c.id,
                "candidate_id": getattr(u, "id", None),
                "name": name,
                "count": cnt,
            }
            pos_id = getattr(c, "position_id", None)
            if pos_id:
                by_pos[pos_id].append(row)
            else:
                flat_results.append(row)

        # Build positions block
        positions = []
        pos_qs = Position.objects.filter(election_id=election_id).order_by("sort", "id")
        for p in pos_qs:
            positions.append({
                "id": p.id,
                "title": p.title,
                "totals": by_pos.get(p.id, []),
            })

        payload = {
            "election": {"id": election.id, "title": getattr(election, "title", None)},
            "positions": positions,
            "results": flat_results,  # at-large fallback
        }
        return Response(payload, status=200)

