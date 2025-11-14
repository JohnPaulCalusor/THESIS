from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from papsas_app.api.permissions import IsAdminOnly
from rest_framework import status

from papsas_app.models import Candidacy, Election


class CurrentElectionView(APIView):
    """
    Minimal 'current election' shim for legacy tests.
    Returns {"id": <election_id>} for active election if any,
    else first election, else creates a placeholder active election.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        e = (
            Election.objects.filter(electionStatus=True).order_by("id").first()
            or Election.objects.order_by("id").first()
        )
        if not e:
            e = Election.objects.create(title="Sample", electionStatus=True, numWinners=1)
        return Response({"id": e.id})


class CandidacyQuickCreate(APIView):
    """
    Test-focused quick-create.
    POST /api/elections/<election_id>/candidacies
    Body expects at least {"member_id": <int>} and may include
    {"credentials": "...", "status": true, "positionId": <int>}
    Only admins can write (IsAdminOnly).
    """
    permission_classes = [IsAdminOnly]

    def post(self, request, election_id: int):
        data = request.data or {}
        member_id = data.get("member_id")
        if not member_id:
            return Response(
                {"code": "INVALID", "message": "Provide member_id or email+name."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cand = Candidacy()
        field_names = {f.name for f in Candidacy._meta.get_fields()}

        if "election" in field_names:
            cand.election_id = int(election_id)

        if "member" in field_names:
            cand.member_id = int(member_id)
        elif "candidateUser" in field_names:
            setattr(cand, "candidateUser_id", int(member_id))
        else:
            return Response(
                {"code": "INVALID", "message": "No suitable member field on Candidacy."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pos_id = data.get("positionId")
        if pos_id is not None and "position" in field_names:
            cand.position_id = int(pos_id)

        if "credentials" in field_names and "credentials" in data:
            cand.credentials = data["credentials"]
        if "status" in field_names and "status" in data:
            cand.status = bool(data["status"])

        cand.save()
        return Response({"id": cand.id, "credentials": getattr(cand, "credentials", "")}, status=status.HTTP_201_CREATED)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAdminOnly])
def candidacy_partial_update(request, pk: int):
    """
    Minimal PATCH/DELETE helper for legacy tests.
    """
    obj = get_object_or_404(Candidacy, pk=pk)
    if request.method == "DELETE":
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    creds = request.data.get("credentials", None)
    if creds is not None:
        obj.credentials = creds
        obj.save(update_fields=["credentials"])
    return Response({"id": obj.id, "credentials": getattr(obj, "credentials", "")})
