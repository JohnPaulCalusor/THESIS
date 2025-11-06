from typing import List, Dict
from django.db import transaction
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Election, Candidacy, Vote

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
        return JsonResponse({"code":"BAD_REQUEST","message":"No candidates provided."}, status=400)
    if election.numWinners and len(cand_ids) > int(election.numWinners):
        return JsonResponse({"code":"BAD_REQUEST","message":f"Select up to {election.numWinners} candidate(s)."}, status=400)

    valid = list(Candidacy.objects.filter(id__in=cand_ids, election=election).values_list("id", flat=True))
    if len(valid) != len(set(cand_ids)):
        return JsonResponse({"code":"BAD_REQUEST","message":"One or more candidates are invalid for this election."}, status=400)

    v = Vote.objects.create(voterID=user, election=election)
    v.candidateID.add(*Candidacy.objects.filter(id__in=valid))
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
    pairs   = _as_pos_pairs(data.get("positions"))

    wants_at_large = bool(atlarge)
    wants_position = bool(pairs)

    if wants_at_large and not wants_position:
        cand_ids = atlarge
    elif wants_position and not wants_at_large:
        cand_ids = [p["candidacy_id"] for p in pairs if p.get("candidacy_id") is not None]
    elif wants_at_large and wants_position:
        cand_ids = [p["candidacy_id"] for p in pairs if p.get("candidacy_id") is not None]
    else:
        return JsonResponse({"code":"BAD_REQUEST","message":"Provide positions[] or atLarge[]"}, status=400)

    return _record_vote(request.user, election, cand_ids)
