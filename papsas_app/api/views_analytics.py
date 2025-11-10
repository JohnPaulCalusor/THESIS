from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOfficerOrAdmin
from .throttles import ExplainPerUserElectionThrottle
from papsas_app.services.results import compute_election_results


class ElectionAnalyticsView(APIView):
    permission_classes = [IsOfficerOrAdmin]

    def get(self, request, election_id: int):
        """
        Analytics totals must exactly match Results.
        Build from the canonical helper and, if analytics needs extra fields,
        compute them from this base dict rather than recounting.
        """
        try:
            base = compute_election_results(election_id)
        except ObjectDoesNotExist:
            return Response({"detail": "Election not found."}, status=status.HTTP_404_NOT_FOUND)

        payload = base
        return Response(payload, status=status.HTTP_200_OK)


class ElectionExplainView(APIView):
    permission_classes = [IsOfficerOrAdmin]
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
