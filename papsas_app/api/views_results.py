from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# If your project relies on global DEFAULT_AUTHENTICATION_CLASSES (SimpleJWT), you can omit the next line.
# If your JSON view sets authentication_classes explicitly, mirror it here as well.
# from rest_framework_simplejwt.authentication import JWTAuthentication

from django.http import HttpResponse
import csv

from papsas_app.services.results import compute_election_results


class ElectionResultsView(APIView):
    """
    JSON: /api/elections/<int:election_id>/results
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    # authentication_classes = [JWTAuthentication]  # uncomment only if your JSON view uses it explicitly

    def get(self, request, election_id: int):
        data = compute_election_results(election_id)
        return Response(data)


class ElectionResultsCsvView(APIView):
    """
    CSV: /api/elections/<int:election_id>/results.csv
         /api/elections/<int:election_id>/results/export.csv (legacy alias)
    Must mirror JSON auth/permissions.
    """
    permission_classes = ElectionResultsView.permission_classes
    # authentication_classes = ElectionResultsView.authentication_classes  # if used above

    def get(self, request, election_id: int):
        data = compute_election_results(election_id)
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="election_{election_id}_results.csv"'
        writer = csv.writer(resp)
        writer.writerow(["position_id", "position_title", "candidacy_id", "candidate_id", "candidate_name", "count"])
        for pos in data.get("positions", []):
            for t in pos.get("totals", []):
                writer.writerow([pos["id"], pos["title"], t["candidacy_id"], t["candidate_id"], t["name"], t["count"]])
        return resp
