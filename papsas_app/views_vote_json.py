import logging
from typing import Dict, List

from django.db import transaction
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Election, Candidacy, Vote, VoteChoice
from .models_position import Position
from papsas_app.utils.election_mode import get_election_mode

logger = logging.getLogger(__name__)

def _as_int_list(v) -> List[int]:
    if isinstance(v, list):
        out = []
        for x in v:
            try:
                out.append(int(x))
            except Exception:
                pass
        return out
    return []

def _as_pos_pairs(v) -> List[Dict[str, int]]:
    out = []
    if isinstance(v, list):
        for it in v:
            if not isinstance(it, dict):
                continue
            cid = it.get("candidacy_id") or it.get("candidacyId")
            pid = it.get("position_id") or it.get("positionId")
            try:
                cid_i = int(cid) if cid is not None else None
                pid_i = int(pid) if pid is not None else None
            except Exception:
                continue
            if cid_i is not None:
                out.append({"candidacy_id": cid_i, "position_id": pid_i})
    return out

def _already_voted(user, election):
    return Vote.objects.filter(voterID=user, election=election).exists()

def _record_vote(user, election, cand_ids: List[int]):
    if _already_voted(user, election):
        return JsonResponse({"code":"ALREADY_VOTED","message":"You already voted."}, status=409)
    if not cand_ids:
        return JsonResponse({"code":"BAD_REQUEST","detail":"No candidates provided."}, status=400)

    valid = list(Candidacy.objects.filter(id__in=cand_ids, election=election).values_list("id", flat=True))
    if len(valid) != len(set(cand_ids)):
        return JsonResponse({"code":"BAD_REQUEST","detail":"One or more candidates are invalid for this election."}, status=400)

    v = Vote.objects.create(voterID=user, election=election)
    v.candidateID.add(*Candidacy.objects.filter(id__in=valid))
    return JsonResponse({"ok": True})


def _record_position_vote(user, election, pairs: List[Dict[str, int]]):
    if _already_voted(user, election):
        return JsonResponse({"code": "ALREADY_VOTED", "message": "You already voted."}, status=409)
    if not pairs:
        return JsonResponse({"code": "BAD_REQUEST", "detail": "No candidates provided."}, status=400)

    candidacy_ids = [p["candidacy_id"] for p in pairs if p.get("candidacy_id") is not None]
    if len(candidacy_ids) != len(pairs):
        return JsonResponse({"code": "BAD_REQUEST", "detail": "Each position entry requires candidacy_id."}, status=400)

    candidacies = (
        Candidacy.objects.filter(id__in=set(candidacy_ids), election=election)
        .select_related("position")
    )
    cand_map = {c.id: c for c in candidacies}
    if len(cand_map) != len(set(candidacy_ids)):
        return JsonResponse(
            {"code": "BAD_REQUEST", "detail": "One or more candidates are invalid for this election."},
            status=400,
        )

    choices = []
    seen = set()
    with transaction.atomic():
        vote = Vote.objects.create(voterID=user, election=election)
        for pair in pairs:
            cid = pair["candidacy_id"]
            pid = pair["position_id"]
            candidacy = cand_map.get(cid)
            if not candidacy:
                return JsonResponse(
                    {"code": "BAD_REQUEST", "detail": f"candidacy_id {cid} not found"},
                    status=400,
                )
            position = getattr(candidacy, "position", None)
            if not position or position.id != pid:
                return JsonResponse(
                    {
                        "code": "BAD_REQUEST",
                        "detail": f"candidacy_id {cid} does not belong to position_id {pid}",
                    },
                    status=400,
                )
            key = (vote.id, candidacy.id)
            if key in seen:
                continue
            seen.add(key)
            choices.append(
                VoteChoice(vote=vote, candidacy=candidacy, position=position)
            )
        VoteChoice.objects.bulk_create(choices)
    return JsonResponse({"ok": True})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def api_vote_json(request, eid: int):
    try:
        election = Election.objects.get(pk=eid, electionStatus=True)
    except Election.DoesNotExist:
        return JsonResponse({"code":"NOT_FOUND","message":"Election not found"}, status=404)

    data = getattr(request, "data", {})
    atlarge = _as_int_list(data.get("atLarge") or data.get("at_large"))
    pairs = _as_pos_pairs(data.get("positions"))

    wants_at_large = bool(atlarge)
    wants_position = bool(pairs)
    mode = get_election_mode(election)

    if mode == "atLarge":
        if not wants_at_large:
            return JsonResponse({"code": "BAD_REQUEST", "detail": "Provide atLarge[]"}, status=400)
        total_picks = len(atlarge)
        logger.info(
            "Vote attempt",
            extra={
                "mode": mode,
                "election_id": election.id,
                "total_picks": total_picks,
                "per_position_counts": {None: total_picks},
            },
        )
        allowed = int(election.numWinners or 0)
        if total_picks > allowed:
            return JsonResponse(
                {
                    "code": "TOO_MANY_AT_LARGE",
                    "detail": f"Select up to {allowed} candidate(s).",
                    "allowed": allowed,
                },
                status=400,
            )
        return _record_vote(request.user, election, atlarge)

    if mode == "positions":
        if not wants_position:
            return JsonResponse({"code": "BAD_REQUEST", "detail": "Provide positions[]"}, status=400)
        if wants_at_large:
            return JsonResponse(
                {"code": "WRONG_MODE", "detail": "This election uses position-based voting."},
                status=400,
            )

        per_pos_counts = {}
        position_ids: set[int] = set()
        for pair in pairs:
            pid = pair.get("position_id")
            if pid is None:
                return JsonResponse(
                    {"code": "BAD_REQUEST", "detail": "position_id is required for positions[]"},
                    status=400,
                )
            per_pos_counts[pid] = per_pos_counts.get(pid, 0) + 1
            position_ids.add(pid)

        positions = {
            pos.id: pos
            for pos in Position.objects.filter(id__in=position_ids)
        }

        cand_ids = [pair["candidacy_id"] for pair in pairs]
        logger.info(
            "Vote attempt",
            extra={
                "mode": mode,
                "election_id": election.id,
                "total_picks": len(cand_ids),
                "per_position_counts": per_pos_counts,
            },
        )

        for pid, count in per_pos_counts.items():
            position = positions.get(pid)
            winners_cap = position.winners if position and position.winners is not None else 1
            if count > winners_cap:
                return JsonResponse(
                    {
                        "code": "TOO_MANY_FOR_POSITION",
                        "detail": "Too many choices for this position.",
                        "position_id": pid,
                        "allowed": winners_cap,
                    },
                    status=400,
                )
        return _record_position_vote(request.user, election, pairs)

    return JsonResponse(
        {"code": "BAD_REQUEST", "detail": "Invalid election voting mode."}, status=400
    )
