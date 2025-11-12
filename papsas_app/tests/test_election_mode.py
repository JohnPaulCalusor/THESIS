from django.test import TestCase
from django.utils import timezone

from papsas_app.models import Election, Position
from papsas_app.utils.election_mode import get_election_mode


class ElectionModeTest(TestCase):
    def _base_election_kwargs(self, **overrides):
        today = timezone.now().date()
        data = dict(
            title="Mode Test",
            startDate=today,
            endDate=today,
            electionStatus=True,
        )
        data.update(overrides)
        return data

    def test_position_winners_nullable(self):
        election = Election.objects.create(**self._base_election_kwargs())
        position = Position.objects.create(election=election, title="Advisers", winners=None)
        self.assertIsNone(position.winners)
        self.assertEqual(position.effective_winners, 1)
        position.winners = 2
        position.save()
        self.assertEqual(position.winners, 2)

    def test_get_election_mode_respects_num_winners(self):
        election_at_large = Election.objects.create(
            **self._base_election_kwargs(title="At-large", numWinners=1)
        )
        election_positions = Election.objects.create(
            **self._base_election_kwargs(title="Positions only", numWinners=None)
        )
        self.assertEqual(get_election_mode(election_at_large), "atLarge")
        self.assertEqual(get_election_mode(election_positions), "positions")
