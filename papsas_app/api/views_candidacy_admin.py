from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsAdminOnly
from ..models import Candidacy
from ..models_position import Position
from .serializers import CandidacyCreateSerializer, CandidacyPatchSerializer

User = get_user_model()


def _cand_row(c: Candidacy):
    u = getattr(c, "candidate", None)
    name = None
    if u:
        name = getattr(u, "get_full_name", lambda: None)() or getattr(u, "username", None) or getattr(u, "email", None)
    return {
        "id": c.id,
        "name": name or getattr(c, "name", f"Candidacy#{c.id}"),
        "email": getattr(u, "email", None),
        "position": ({"id": getattr(c, "position_id", None), "title": getattr(getattr(c, "position", None), "title", None)} if getattr(c, "position_id", None) else None),
        "positionId": getattr(c, "position_id", None),
        "positionTitle": getattr(getattr(c, "position", None), "title", None),
        "credentials": getattr(c, "credentials", ""),
        "status": bool(getattr(c, "candidacyStatus", True)),
    }


class CandidacyListCreateView(APIView):
    permission_classes = [IsAdminOnly]

    def get(self, request, election_id):
        qs = Candidacy.objects.select_related("candidate", "position").filter(election_id=election_id).order_by("id")
        items = [_cand_row(c) for c in qs]
        return Response({"results": items})

    def post(self, request, election_id):
        s = CandidacyCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        # Resolve/create user
        if d.get("member_id"):
            user = get_object_or_404(User, pk=d["member_id"])
        else:
            email = d["email"].lower()
            defaults = {"email": email, "is_active": True}
            name = (d.get("name") or "").strip()
            if name:
                # best-effort split
                first, last = name, ""
                if "," in name:
                    last, first = [p.strip() for p in name.split(",", 1)]
                elif " " in name:
                    first, last = name.rsplit(" ", 1)
                defaults["first_name"] = first
                defaults["last_name"] = last
            user, _ = User.objects.get_or_create(username=email, defaults=defaults)

        pos = None
        if d.get("position_id"):
            pos = get_object_or_404(Position, pk=d["position_id"])

        # Unique guard
        if Candidacy.objects.filter(election_id=election_id, candidate=user, position=pos).exists():
            return Response({"code": "ALREADY_EXISTS", "message": "Candidacy already exists for this election/position."}, status=status.HTTP_409_CONFLICT)

        c = Candidacy.objects.create(election_id=election_id, candidate=user, position=pos)
        return Response(_cand_row(c), status=status.HTTP_201_CREATED)


class CandidacyDetailPatchView(APIView):
    permission_classes = [IsAdminOnly]

    def patch(self, request, election_id, pk):
        c = get_object_or_404(Candidacy, pk=pk, election_id=election_id)
        s = CandidacyPatchSerializer(data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        if "position_id" in d:
            c.position = get_object_or_404(Position, pk=d["position_id"]) if d["position_id"] is not None else None
        if "candidacyStatus" in d:
            c.candidacyStatus = bool(d["candidacyStatus"])
        if "credentials" in d:
            c.credentials = d["credentials"]

        # ensure uniqueness
        if Candidacy.objects.exclude(pk=c.pk).filter(election_id=election_id, candidate=c.candidate, position=c.position).exists():
            return Response({"code": "ALREADY_EXISTS", "message": "Candidacy already exists for this election/position."}, status=status.HTTP_409_CONFLICT)

        c.save()
        return Response({"ok": True})

