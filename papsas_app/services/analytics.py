from typing import Any, Dict, List, Union

from papsas_app.models import Election, Vote
from papsas_app.services.results import compute_election_results


def compute_election_analytics(
    election_or_id: Union[int, str, Election]
) -> Dict[str, Any]:
    base = compute_election_results(election_or_id)
    election = base.get("election") or {}
    election_id = election.get("id")

    positions = base.get("positions") or []
    total_votes = 0
    by_position: List[Dict[str, Any]] = []
    by_candidate: List[Dict[str, Any]] = []

    for position in positions:
        totals = position.get("totals") or []
        pos_total = sum(int(t.get("count") or 0) for t in totals)
        total_votes += pos_total
        by_position.append({
            "position_id": position.get("id"),
            "title": position.get("title"),
            "total": pos_total,
        })
        for total in totals:
            by_candidate.append({
                "candidacy_id": total.get("candidacy_id"),
                "candidate_id": total.get("candidate_id"),
                "name": total.get("name"),
                "count": int(total.get("count") or 0),
                "position_id": position.get("id"),
            })

    ballots_cast = 0
    if election_id is not None:
        ballots_cast = (
            Vote.objects
            .filter(
                election_id=election_id,
                candidateID__position__isnull=False,
            )
            .values("voterID")
            .distinct()
            .count()
        )

    selections_total = total_votes

    return {
        "election": election,
        "total_votes": total_votes,
        "ballots_cast": ballots_cast,
        "selections_total": selections_total,
        "by_position": by_position,
        "by_candidate": by_candidate,
    }


# Local check (copy/paste into shell if needed):
# from papsas_app.services.analytics import compute_election_analytics as ca
# print(ca(1))
