# papsas_app/api/views_ballot.py
from django.apps import apps
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
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
    # 👇 Make this endpoint completely public / auth-free
    authentication_classes: list = []
    permission_classes = [AllowAny]

    def perform_authentication(self, request):
        """
        Override DRF's default behaviour so it does NOT run DEFAULT_AUTHENTICATION_CLASSES.
        This prevents AUTH_REQUIRED from being raised for anonymous ballot reads.
        """
        return

    @staticmethod
    def _build_metadata(candidates, request):
        """
        Build a per-candidacy metadata map:
        {
          candidacy_id: {
            "credentials": "...",
            "photoUrl": "https://...",
            "name": "Nice Display Name",
            "bio": "...",
            "platform": "..."
          }
        }
        """
        metadata: dict[int, dict[str, str | None]] = {}

        for c in candidates:
            candidate = getattr(c, "candidate", None)

            # Prefer explicit credentials; fall back to other descriptive fields
            raw_creds = (
                getattr(c, "credentials", None)
                or getattr(c, "bio", None)
                or getattr(c, "platform", None)
            )
            credentials = str(raw_creds).strip() if raw_creds else None

            # Photo: primarily candidate.profilePic; safely turned into absolute URL
            photo_url: str | None = None
            if candidate is not None:
                profile_pic = getattr(candidate, "profilePic", None)
                if profile_pic is not None:
                    raw = getattr(profile_pic, "url", profile_pic)
                    if isinstance(raw, str):
                        photo_url = raw

            if photo_url and request:
                try:
                    photo_url = request.build_absolute_uri(photo_url)
                except Exception:
                    # Don't blow up ballot if URL building fails
                    pass

            metadata[c.id] = {
                "credentials": credentials,
                "photoUrl": photo_url,
                "name": display_name(candidate) or getattr(c, "name", "") or f"Candidacy#{c.id}",
                "bio": getattr(c, "bio", None),
                "platform": getattr(c, "platform", None),
            }

        return metadata

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
            .filter(election_id=election_id)
        )

        metadata = self._build_metadata(cands, request)

        # group choices per position
        by_pos: dict[int, list[dict]] = {}
        at_large: list[dict] = []

        for c in cands:
            u = getattr(c, "candidate", None)
            meta = metadata.get(c.id, {})

            name = (
                meta.get("name")
                or display_name(u)
                or getattr(c, "name", f"Candidacy#{c.id}")
            )

            item: dict[str, object] = {
                # include both camelCase and snake_case keys to be frontend-friendly
                "candidacyId": c.id,
                "candidacy_id": c.id,
                "candidateId": getattr(u, "id", None),
                "candidate_id": getattr(u, "id", None),
                "name": name,
            }

            # Only attach these if non-empty so the JSON stays tidy.
            if meta.get("credentials"):
                item["credentials"] = meta["credentials"]
            if meta.get("bio"):
                item["bio"] = meta["bio"]
            if meta.get("platform"):
                item["platform"] = meta["platform"]
            if meta.get("photoUrl"):
                item["photoUrl"] = meta["photoUrl"]

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
