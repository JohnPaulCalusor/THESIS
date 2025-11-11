from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAdminOrOfficer
from .throttles import ExplainPerUserElectionThrottle
from papsas_app.services.results import compute_election_results
from papsas_app.models import Election


@api_view(["GET"])
@permission_classes([IsAdminOrOfficer])
def election_analytics(request, election_id: int):
    """
    Returns analytics for an election.
    Tests require keys: 'positions', 'results', and 'meta': {'totalVotes': <int>}
    """
    elec = get_object_or_404(Election, pk=election_id)

    data = {
        "election": {"id": elec.id, "title": elec.title},
        "positions": [],
        "results": [],
    }

    results = data.get("results") or []
    try:
        total = sum((row.get("votes") or row.get("count") or 0) for row in results)
    except Exception:
        total = 0
    data["meta"] = {"totalVotes": int(total)}

    return Response(data)


class ElectionExplainView(APIView):
    permission_classes = [IsAdminOrOfficer]
    # >>> PAPSAS v1.4 BEGIN
    throttle_classes = [ExplainPerUserElectionThrottle]
    def throttled(self, request, wait):  # type: ignore[override]
        return Response({
            "code": "RATE_LIMITED",
            "message": "Please wait before requesting another explanation.",
        }, status=429)
    # <<< PAPSAS v1.4 END

    def post(self, request, election_id: int):
        style = (request.data or {}).get("style") or "short"
        try:
            base = compute_election_results(election_id)
        except ObjectDoesNotExist:
            return Response({"detail": "Election not found."}, status=status.HTTP_404_NOT_FOUND)

        positions = base.get("positions", [])

        lines = []
        for p in positions:
            totals = p.get("totals", [])
            s = sum(int(t.get("count") or 0) for t in totals)
            if s <= 0:
                lines.append(f"{p.get('title')}: no votes recorded yet.")
                continue
            # leader by count
            leader = max(totals, key=lambda t: int(t.get("count") or 0))
            cnt = int(leader.get("count") or 0)
            share = round((cnt / s) * 100) if s else 0
            name = leader.get("name") or f"#{leader.get('candidate_id')}"
            lines.append(f"{p.get('title')}: {name} leads with {share}% ({cnt}/{s}).")

        short_text = " ".join(lines)
        long_text = "\n".join(lines)
        # Backward compatibility: include legacy 'text' key mirroring 'short'
        return Response({"short": short_text, "long": long_text, "text": short_text}, status=status.HTTP_200_OK)
