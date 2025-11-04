from collections import defaultdict
from typing import Tuple, List, Dict, Any

from django.apps import apps
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsOfficerOrAdmin

Election  = apps.get_model("papsas_app", "Election")
Candidacy = apps.get_model("papsas_app", "Candidacy")
Position  = apps.get_model("papsas_app", "Position")
VoteSel   = apps.get_model("papsas_app", "VoteSelection")
Vote      = apps.get_model("papsas_app", "Vote")
User      = apps.get_model("papsas_app", "User")


def display_name(u):
    parts = [getattr(u, "first_name", "") or "", getattr(u, "last_name", "") or ""]
    pretty = " ".join(p for p in parts if p).strip()
    return pretty or getattr(u, "email", "") or getattr(u, "username", "") or f"User#{getattr(u, 'pk', '0')}"


def pick_fk(model, target_model, preferred_names=()):
    fields = list(model._meta.get_fields())
    for f in fields:
        if getattr(f, "is_relation", False) and getattr(f, "related_model", None) is target_model and getattr(f, "many_to_one", False):
            return f.name
        if getattr(f, "is_relation", False) and getattr(f, "related_model", None) is target_model and type(f).__name__ == "OneToOneField":
            return f.name
    names = {f.name for f in fields}
    for name in preferred_names:
        if name in names:
            return name
    return None


# Detect key FKs similarly to views_results
VSEL_USER_FK = pick_fk(VoteSel, User, ("candidate", "user"))
VSEL_VOTE_FK = pick_fk(VoteSel, Vote, ("vote",))
VOTE_ELECT_FK= pick_fk(Vote, Election, ("election", "election_id"))
CAND_USER_FK = pick_fk(Candidacy, User, ("candidate", "user", "candidate_user", "nominee"))
CAND_POS_FK  = pick_fk(Candidacy, Position, ("position",))
CAND_ELECT_FK= pick_fk(Candidacy, Election, ("election", "election_id"))


def compute_positions(election_id: int) -> Tuple[List[Dict[str, Any]], int]:
    """Return (positions_with_totals, total_votes)
    positions_with_totals: [{id,title, totals:[{candidate_id,name,count}]}]
    total_votes: sum of counts across all selections (best-effort)
    """
    # Guard for schema requirements
    if not (VSEL_USER_FK and VSEL_VOTE_FK and VOTE_ELECT_FK and CAND_USER_FK):
        return [], 0

    user_id_key = f"{VSEL_USER_FK}_id"
    election_filter = {f"{VSEL_VOTE_FK}__{VOTE_ELECT_FK}_id": election_id}
    user_tallies = {
        row[user_id_key]: row["count"]
        for row in (VoteSel.objects
                    .filter(**election_filter)
                    .values(user_id_key)
                    .annotate(count=Count("id")))
    }

    cand_qs_filter = {f"{CAND_ELECT_FK}_id": election_id} if CAND_ELECT_FK else {"election_id": election_id}
    sr = [CAND_USER_FK]
    if CAND_POS_FK:
        sr.append(CAND_POS_FK)
    cands = Candidacy.objects.select_related(*sr).filter(**cand_qs_filter)

    cand_by_user: Dict[int, Any] = {}
    for c in cands:
        uid = getattr(getattr(c, CAND_USER_FK), "id", None)
        if uid is not None and uid not in cand_by_user:
            cand_by_user[uid] = c

    by_pos = defaultdict(list)
    for uid, cnt in user_tallies.items():
        c = cand_by_user.get(uid)
        if not c:
            # skip unknowns here; results view exposes at-large separately
            continue
        u = getattr(c, CAND_USER_FK)
        name = display_name(u) if u else getattr(c, "name", f"Candidacy#{c.id}")
        row = {"candidacy_id": c.id, "candidate_id": getattr(u, "id", None), "name": name, "count": cnt}
        pos_id = getattr(c, f"{CAND_POS_FK}_id", None) if CAND_POS_FK else None
        if pos_id:
            by_pos[pos_id].append(row)

    positions = []
    total_votes = 0
    if CAND_POS_FK:
        pos_qs_filter = cand_qs_filter
        for p in Position.objects.filter(**pos_qs_filter).order_by("sort", "id"):
            totals = by_pos.get(p.id, [])
            # accumulate total votes across all positions
            for t in totals:
                total_votes += int(t.get("count") or 0)
            positions.append({"id": p.id, "title": p.title, "totals": totals})

    # Fallback for total_votes using Vote table if available and FK exists
    if total_votes == 0 and VOTE_ELECT_FK:
        total_votes = Vote.objects.filter(**{f"{VOTE_ELECT_FK}_id": election_id}).count()

    return positions, total_votes


class ElectionAnalyticsView(APIView):
    permission_classes = [IsOfficerOrAdmin]

    def get(self, request, election_id: int):
        try:
            e = Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({"detail": "Election not found."}, status=404)

        positions, total_votes = compute_positions(election_id)

        # add share per position
        out_positions: List[Dict[str, Any]] = []
        for p in positions:
            totals = p.get("totals", [])
            s = sum(int(t.get("count") or 0) for t in totals) or 0
            enriched = []
            for t in totals:
                cnt = int(t.get("count") or 0)
                share = (cnt / s) if s else 0.0
                enriched.append({
                    "candidate_id": t.get("candidate_id"),
                    "name": t.get("name"),
                    "count": cnt,
                    "share": share,
                })
            out_positions.append({"id": p.get("id"), "title": p.get("title"), "totals": enriched})

        payload = {
            "election": {"id": e.id, "title": getattr(e, "title", None)},
            "positions": out_positions,
            "meta": {"totalVotes": int(total_votes)},
        }
        return Response(payload, status=200)


class ElectionExplainView(APIView):
    permission_classes = [IsOfficerOrAdmin]

    def post(self, request, election_id: int):
        style = (request.data or {}).get("style") or "short"
        try:
            Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({"detail": "Election not found."}, status=404)

        positions, total_votes = compute_positions(election_id)

        lines: List[str] = []
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
        return Response({"short": short_text, "long": long_text, "text": short_text}, status=200)
