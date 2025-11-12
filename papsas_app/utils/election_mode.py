from __future__ import annotations


def get_election_mode(election) -> str:
    """Return the configuration mode implied by the election."""
    num_winners = getattr(election, "numWinners", None)
    return "atLarge" if (num_winners or 0) > 0 else "positions"
