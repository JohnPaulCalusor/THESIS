from collections import defaultdict
from django.apps import apps
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOfficerOrAdmin
from rest_framework.response import Response

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
        # allow OneToOne (e.g., VoteSelection.vote)
        if getattr(f, "is_relation", False) and getattr(f, "related_model", None) is target_model and type(f).__name__ == "OneToOneField":
            return f.name
    names = {f.name for f in fields}
    for name in preferred_names:
        if name in names:
            return name
    return None

# Detect the relevant links
VSEL_USER_FK = pick_fk(VoteSel, User, ("candidate", "user"))
VSEL_VOTE_FK = pick_fk(VoteSel, Vote, ("vote",))
VOTE_ELECT_FK= pick_fk(Vote, Election, ("election", "election_id"))
CAND_USER_FK = pick_fk(Candidacy, User, ("candidate", "user", "candidate_user", "nominee"))
CAND_POS_FK  = pick_fk(Candidacy, Position, ("position",))
CAND_ELECT_FK= pick_fk(Candidacy, Election, ("election", "election_id"))

class ElectionResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, election_id: int):
        try:
            election = Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({"detail": "Election not found."}, status=404)

        # Hard requirements for this schema pattern
        if not (VSEL_USER_FK and VSEL_VOTE_FK and VOTE_ELECT_FK and CAND_USER_FK):
            return Response({
                "election": {"id": election.id, "title": getattr(election, "title", None)},
                "positions": [],
                "results": [],
                "note": "Missing FK(s): need VoteSelection→User, VoteSelection→Vote, Vote→Election, and Candidacy→User."
            }, status=200)

        # 1) Tally votes per USER, restricted to this election via Vote
        user_id_key = f"{VSEL_USER_FK}_id"
        election_filter = {f"{VSEL_VOTE_FK}__{VOTE_ELECT_FK}_id": election_id}
        user_tallies = {
            row[user_id_key]: row["count"]
            for row in (VoteSel.objects
                        .filter(**election_filter)
                        .values(user_id_key)
                        .annotate(count=Count("id")))
        }

        # 2) Map user -> candidacy for this election
        cand_qs_filter = {f"{CAND_ELECT_FK}_id": election_id} if CAND_ELECT_FK else {"election_id": election_id}
        sr = [CAND_USER_FK]
        if CAND_POS_FK:
            sr.append(CAND_POS_FK)
        cands = (Candidacy.objects.select_related(*sr).filter(**cand_qs_filter))

        # Build a dict of user_id -> candidacy object (assumes one candidacy per user per election)
        cand_by_user = {}
        for c in cands:
            uid = getattr(getattr(c, CAND_USER_FK), "id", None)
            if uid is not None and uid not in cand_by_user:
                cand_by_user[uid] = c

        # 3) Convert user tallies into candidacy tallies
        by_pos = defaultdict(list)
        flat_results = []

        for uid, cnt in user_tallies.items():
            c = cand_by_user.get(uid)
            if not c:
                # vote for a user who is not a candidate in this election — ignore or surface as at-large
                flat_results.append({"candidacy_id": None, "candidate_id": uid, "name": f"User#{uid}", "count": cnt})
                continue

            u = getattr(c, CAND_USER_FK)
            name = display_name(u) if u else getattr(c, "name", f"Candidacy#{c.id}")
            row = {
                "candidacy_id": c.id,
                "candidate_id": getattr(u, "id", None),
                "name": name,
                "count": cnt,
            }
            pos_id = getattr(c, f"{CAND_POS_FK}_id", None) if CAND_POS_FK else None
            (by_pos[pos_id].append(row) if pos_id else flat_results.append(row))

        # 4) Build positions block if we can see a position FK
        positions = []
        if CAND_POS_FK:
            pos_qs_filter = cand_qs_filter  # same election scoping
            for p in Position.objects.filter(**pos_qs_filter).order_by("sort", "id"):
                positions.append({"id": p.id, "title": p.title, "totals": by_pos.get(p.id, [])})

        return Response({
            "election": {"id": election.id, "title": getattr(election, "title", None)},
            "positions": positions,
            "results": flat_results
        }, status=200)

import csv
from django.http import HttpResponse


class ElectionResultsCsvView(APIView):
    permission_classes = [IsOfficerOrAdmin]

    def get(self, request, election_id: int):
        try:
            Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({"detail": "Election not found."}, status=404)

        # Recompute similarly to JSON view
        # 1) user tallies in election
        if not (VSEL_USER_FK and VSEL_VOTE_FK and VOTE_ELECT_FK and CAND_USER_FK):
            # >>> PAPSAS v1.4 BEGIN
            resp = HttpResponse(content_type="text/csv; charset=utf-8")
            resp["Content-Disposition"] = f'attachment; filename="results-election-{election_id}.csv"'
            # <<< PAPSAS v1.4 END
            csv.writer(resp).writerow(["position_id", "position_title", "candidate_id", "candidate_name", "count"])
            return resp

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
        cands = (Candidacy.objects.select_related(*sr).filter(**cand_qs_filter))

        cand_by_user = {}
        for c in cands:
            uid = getattr(getattr(c, CAND_USER_FK), "id", None)
            if uid is not None and uid not in cand_by_user:
                cand_by_user[uid] = c

        # Build positions map: id -> title
        pos_titles = {}
        if CAND_POS_FK:
            for p in Position.objects.filter(**cand_qs_filter).order_by("sort", "id"):
                pos_titles[p.id] = p.title

        # >>> PAPSAS v1.4 BEGIN
        resp = HttpResponse(content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="results-election-{election_id}.csv"'
        # <<< PAPSAS v1.4 END
        w = csv.writer(resp)
        w.writerow(["position_id", "position_title", "candidate_id", "candidate_name", "count"])

        for uid, cnt in user_tallies.items():
            c = cand_by_user.get(uid)
            if not c:
                w.writerow(["", "", uid, f"User#{uid}", cnt])
                continue
            u = getattr(c, CAND_USER_FK)
            cand_name = (getattr(u, "get_full_name", lambda: None)() or getattr(u, "username", None) or getattr(u, "email", None) or f"User#{uid}")
            pos_id = getattr(c, f"{CAND_POS_FK}_id", None) if CAND_POS_FK else None
            w.writerow([pos_id or "", pos_titles.get(pos_id, "") if pos_id else "", getattr(u, "id", None), cand_name, cnt])
        return resp
