from typing import Any, Dict, List, Optional, Union

from django.apps import apps
from django.db.models import Count

from papsas_app.models import Candidacy, Election, Vote, VoteChoice


def _normalize_election(election_or_id: Union[int, str, Election]) -> Election:
    if isinstance(election_or_id, Election):
        return election_or_id
    if election_or_id in (None, "", 0):
        raise ValueError("compute_election_results: invalid election id")
    try:
        eid = int(election_or_id)
    except (TypeError, ValueError):
        raise ValueError(
            f"compute_election_results: cannot coerce id from {election_or_id!r}"
        )
    return Election.objects.get(id=eid)


def _aggregate_from_votechoice(election: Election) -> Optional[Dict[int, Dict[str, Any]]]:
    rows = list(
        VoteChoice.objects.filter(vote__election=election)
        .values("candidacy_id")
        .annotate(count=Count("id"))
    )
    if not rows:
        return None

    cand_ids = [r["candidacy_id"] for r in rows]
    cands = {
        c.id: c
        for c in Candidacy.objects.filter(id__in=cand_ids)
        .select_related("position", "candidate")
    }

    by_pos: Dict[int, Dict[str, Any]] = {}
    for row in rows:
        cand = cands.get(row["candidacy_id"])
        if not cand or not getattr(cand, "position", None):
            continue
        pos = cand.position
        entry = by_pos.setdefault(
            pos.id, {"id": pos.id, "title": pos.title, "totals": []}
        )
        name = (
            getattr(cand.candidate, "email", None)
            or getattr(cand.candidate, "username", None)
            or f"candidacy#{cand.id}"
        )
        entry["totals"].append({
            "candidacy_id": cand.id,
            "candidate_id": getattr(cand.candidate, "id", None),
            "name": name,
            "count": row["count"],
        })
    return by_pos


def _aggregate_from_legacy(election: Election) -> Dict[int, Dict[str, Any]]:
    vf = Vote._meta.get_field("candidateID")
    through = vf.remote_field.through

    vote_fk = None
    cand_fk = None
    for f in through._meta.fields:
        rm = getattr(getattr(f, "remote_field", None), "model", None)
        if rm is Vote:
            vote_fk = f.name
        if rm is Candidacy:
            cand_fk = f.name
    if not vote_fk or not cand_fk:
        raise RuntimeError("Could not inspect Vote.candidateID through table.")

    rows = (
        through.objects
        .filter(**{f"{vote_fk}__election_id": election.id, f"{cand_fk}__isnull": False})
        .values(cand_fk)
        .annotate(count=Count("id"))
        .order_by()
    )

    cand_ids = [row[cand_fk] for row in rows]
    cands = {
        c.id: c
        for c in Candidacy.objects.filter(id__in=cand_ids)
        .select_related("position", "candidate")
    }

    by_pos: Dict[int, Dict[str, Any]] = {}
    for row in rows:
        cand = cands.get(row[cand_fk])
        if not cand or not getattr(cand, "position", None):
            continue
        pos = cand.position
        entry = by_pos.setdefault(
            pos.id, {"id": pos.id, "title": pos.title, "totals": []}
        )
        name = (
            getattr(cand.candidate, "email", None)
            or getattr(cand.candidate, "username", None)
            or f"candidacy#{cand.id}"
        )
        entry["totals"].append({
            "candidacy_id": cand.id,
            "candidate_id": getattr(cand.candidate, "id", None),
            "name": name,
            "count": row["count"],
        })
    return by_pos


def compute_election_results(
    election_or_id: Union[int, str, Election]
) -> Dict[str, Any]:
    election = _normalize_election(election_or_id)
    by_pos = _aggregate_from_votechoice(election)
    if by_pos is None:
        by_pos = _aggregate_from_legacy(election)

    LABEL = "papsas_app"
    Position = apps.get_model(LABEL, "Position")

    positions = Position.objects.filter(election_id=election.id).values("id", "title")
    out_positions: List[Dict[str, Any]] = []
    for pos in positions:
        entry = by_pos.get(pos["id"])
        if entry:
            entry["totals"].sort(key=lambda x: (-x["count"], x["name"]))
            out_positions.append(entry)
        else:
            out_positions.append({"id": pos["id"], "title": pos["title"], "totals": []})

    return {
        "election": {"id": election.id, "title": election.title},
        "positions": out_positions,
        "results": [],
    }
