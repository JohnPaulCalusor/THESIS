from typing import List, Dict
from django.conf import settings
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

def _debug_vote_failure(election_id, payload, reason, errors=None):
    if settings.DEBUG:
        print(f"DEBUG /elections/{election_id}/vote payload:", payload)
        print(f"DEBUG /elections/{election_id}/vote errors:", errors or reason)

def _bad_request_response(election_id, payload, reason, errors=None, code="BAD_REQUEST"):
    _debug_vote_failure(election_id, payload, reason, errors)
    if settings.DEBUG:
        return JsonResponse({"detail": reason, "errors": errors or [], "payload": payload}, status=400)
    return JsonResponse({"code": code, "message": reason}, status=400)

def _find_duplicate_positions(pairs: List[Dict[str, int]]) -> List[int | None]:
    seen: dict[int | None, bool] = {}
    duplicates: list[int | None] = []
    for entry in pairs:
        pid = entry.get("position_id")
        if pid in seen:
            if pid not in duplicates:
                duplicates.append(pid)
        else:
            seen[pid] = True
    return duplicates

def _record_vote(user, election, cand_ids: List[int], payload, enforce_limit=True):
    if _already_voted(user, election):
        return JsonResponse({"code":"ALREADY_VOTED","message":"You already voted."}, status=409)
    if not cand_ids:
        return _bad_request_response(election.id, payload, "No candidates provided.")
    if election.numWinners and len(cand_ids) > int(election.numWinners):
        if enforce_limit:
            return _bad_request_response(
                election.id,
                payload,
                f"Select up to {election.numWinners} candidate(s).",
                errors=cand_ids,
            )

    valid = list(Candidacy.objects.filter(id__in=cand_ids, election=election).values_list("id", flat=True))
    if len(valid) != len(set(cand_ids)):
        return _bad_request_response(
            election.id,
            payload,
            "One or more candidates are invalid for this election.",
            errors=cand_ids,
        )

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

    # Payload: prefer {"positions": [{"position_id": <int?>, "candidacy_id": <int>}, ...]} but also accept {"atLarge": [<int>, ...]} and snake_case variants; at least one candidacy_id is required.
    data = getattr(request, "data", {})
    positions = _as_pos_pairs(data.get("positions"))
    if positions:
        duplicates = _find_duplicate_positions(positions)
        if duplicates:
            return _bad_request_response(
                election.id,
                data,
                "You may only select one candidate per position.",
                errors=duplicates,
            )
        cand_ids = [p["candidacy_id"] for p in positions if p.get("candidacy_id") is not None]
        return _record_vote(request.user, election, cand_ids, data, enforce_limit=False)
    atlarge = _as_int_list(data.get("atLarge") or data.get("at_large"))
    if atlarge:
        return _record_vote(request.user, election, atlarge, data)
    return _bad_request_response(election.id, data, "Provide positions[] or atLarge[]")
