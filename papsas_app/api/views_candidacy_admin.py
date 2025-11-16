from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .permissions import IsAdminOnly, IsAdminWrite, IsOfficerOrAdmin, IsOfficerOrAdminRead
from ..models import Candidacy, Position  # adjust import if your models path differs
from .serializers import CandidacyCreateSerializer, CandidacyPatchSerializer
from papsas_app.analytics.audit import log_event

User = get_user_model()

def _serialize_candidacy(c: Candidacy):
    u = c.candidate
    pos = c.position
    # Keep the shape your admin page already consumes
    return {
        "id": c.id,
        "candidacyStatus": getattr(c, "candidacyStatus", True),
        "credentials": getattr(c, "credentials", None),
        "candidate": {
            "id": u.id,
            "name": (getattr(u, "get_full_name", lambda: None)() or getattr(u, "username", "")),
            "email": getattr(u, "email", ""),
            "username": getattr(u, "username", ""),
        },
        "position": ({"id": pos.id, "title": pos.title} if pos else None),
}


def _try_log_candidacy_event(request, action, c_obj, status_label="success"):
    if not c_obj:
        return
    try:
        log_event(
            request,
            action=action,
            status=status_label,
            scope_election_id=getattr(c_obj, "election_id", None),
            target_type="candidacy",
            target_id=str(getattr(c_obj, "id", "")),
        )
    except Exception:
        pass

# --- Read-only list (keep existing behavior; officers may read if you prefer) ---
class CandidacyListView(APIView):
    def get_permissions(self):
        # Officers/Admin can READ; only Admin can WRITE
        if self.request.method in ("GET","HEAD","OPTIONS"):
            return [IsOfficerOrAdmin()]
        return [IsAdminOnly()]
    permission_classes = [IsAdminOnly]  # or [IsOfficerOrAdmin] if officers should read
    def get(self, request, election_id: int):
        qs = (Candidacy.objects
              .filter(election_id=election_id)
              .select_related("candidate", "position")
              .order_by("id"))
        return Response({"results": [_serialize_candidacy(c) for c in qs]})

# --- New: admin-only GET (reuses list) + POST create ---
class CandidacyListCreateView(APIView):
    permission_classes = [IsAdminOnly]

    def get_permissions(self):
        # Officers/Admin can READ; only Admin can WRITE
        if self.request.method in ("GET","HEAD","OPTIONS"):
            return [IsOfficerOrAdmin()]
        return [IsAdminOnly()]
    def get(self, request, election_id: int):
        return CandidacyListView().get(request, election_id=election_id)

    def post(self, request, election_id: int):
        s = CandidacyCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        # Resolve/create user
        if d.get("member_id"):
            user = get_object_or_404(User, pk=d["member_id"])
        else:
            email = d["email"].lower()
            defaults = {"email": email, "is_active": True}
            if d.get("name"):
                defaults["first_name"] = d["name"]
            user, _ = User.objects.get_or_create(username=email, defaults=defaults)

        # Optional position
        pos = None
        if "position_id" in d and d["position_id"]:
            pos = get_object_or_404(Position, pk=d["position_id"])

        # Unique (election, candidate, position)
        if Candidacy.objects.filter(election_id=election_id, candidate=user, position=pos).exists():
            return Response(
                {"code": "ALREADY_EXISTS", "message": "Candidacy already exists for this election/position."},
                status=status.HTTP_409_CONFLICT,
            )

        c = Candidacy.objects.create(election_id=election_id, candidate=user, position=pos)
        _try_log_candidacy_event(request, "CANDIDACY_CREATED", c)
        return Response(_serialize_candidacy(c), status=status.HTTP_201_CREATED)

# --- New: admin-only PATCH ---
class CandidacyDetailPatchView(APIView):
    permission_classes = [IsAdminOnly]

    def patch(self, request, election_id: int, pk: int):
        c = get_object_or_404(Candidacy, pk=pk, election_id=election_id)
        s = CandidacyPatchSerializer(data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        if "position_id" in d:
            c.position = get_object_or_404(Position, pk=d["position_id"]) if d["position_id"] is not None else None
        if "candidacyStatus" in d:
            c.candidacyStatus = d["candidacyStatus"]
        if "credentials" in d:
            c.credentials = d["credentials"]

        # Guard duplicates
        if Candidacy.objects.exclude(pk=c.pk).filter(
            election_id=election_id, candidate=c.candidate, position=c.position
        ).exists():
            return Response(
                {"code": "ALREADY_EXISTS", "message": "Candidacy already exists for this election/position."},
                status=status.HTTP_409_CONFLICT,
            )

        c.save(update_fields=["position", "candidacyStatus", "credentials"])
        _try_log_candidacy_event(request, "CANDIDACY_UPDATED", c)
        return Response({"ok": True})
