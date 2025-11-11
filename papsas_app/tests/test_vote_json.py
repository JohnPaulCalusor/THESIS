from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from papsas_app.models import Election, Candidacy, Vote
from papsas_app.models_position import Position


class VoteJsonTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()

        self.atlarge_election = Election.objects.create(
            title="At-large race",
            startDate="2025-11-01",
            endDate="2025-11-05",
            electionStatus=True,
            numWinners=1,
        )
        self.atlarge_cand1 = Candidacy.objects.create(
            election=self.atlarge_election,
            candidate=self._create_user("cand-at-1"),
            candidacyStatus=True,
        )
        self.atlarge_cand2 = Candidacy.objects.create(
            election=self.atlarge_election,
            candidate=self._create_user("cand-at-2"),
            candidacyStatus=True,
        )

        self.position_election = Election.objects.create(
            title="Positions race",
            startDate="2025-11-01",
            endDate="2025-11-05",
            electionStatus=True,
            numWinners=None,
        )
        self.position_one = Position.objects.create(
            election=self.position_election,
            title="Lead",
            winners=1,
        )
        self.position_two = Position.objects.create(
            election=self.position_election,
            title="Support",
            winners=1,
        )
        self.position_cand1 = Candidacy.objects.create(
            election=self.position_election,
            candidate=self._create_user("cand-pos-1"),
            candidacyStatus=True,
            position=self.position_one,
        )
        self.position_cand2 = Candidacy.objects.create(
            election=self.position_election,
            candidate=self._create_user("cand-pos-2"),
            candidacyStatus=True,
            position=self.position_one,
        )
        self.position_cand3 = Candidacy.objects.create(
            election=self.position_election,
            candidate=self._create_user("cand-pos-3"),
            candidacyStatus=True,
            position=self.position_two,
        )

    def _create_user(self, suffix: str):
        # Explicit unique email to satisfy User.email unique constraint in tests
        return self.User.objects.create_user(
            username=f"user-{suffix}",
            email=f"user-{suffix}@test.local",
            password="pass",
        )

    def _post_vote(self, user, election, payload):
        self.client.force_authenticate(user=user)
        return self.client.post(f"/api/elections/{election.id}/vote", payload, format="json")

    def test_vote_atlarge_legacy_ok(self):
        voter = self._create_user("voter-at-large-1")
        res = self._post_vote(voter, self.atlarge_election, {"atLarge": [self.atlarge_cand1.id]})
        self.assertEqual(res.status_code, 200)
        vote = Vote.objects.get(voterID=voter, election=self.atlarge_election)
        self.assertEqual(vote.candidateID.count(), 1)

        voter_positions = self._create_user("voter-at-large-positions")
        res = self._post_vote(
            voter_positions,
            self.atlarge_election,
            {"positions": [{"candidacyId": self.atlarge_cand2.id, "positionId": None}]},
        )
        self.assertEqual(res.status_code, 200)
        vote = Vote.objects.get(voterID=voter_positions, election=self.atlarge_election)
        self.assertEqual(vote.candidateID.count(), 1)

        overflow_voter = self._create_user("voter-at-large-overflow")
        res = self._post_vote(
            overflow_voter,
            self.atlarge_election,
            {"atLarge": [self.atlarge_cand1.id, self.atlarge_cand2.id]},
        )
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data["code"], "TOO_MANY_AT_LARGE")
        self.assertEqual(data["allowed"], 1)
        self.assertEqual(data["detail"], "Select up to 1 candidate(s).")
        self.assertFalse(Vote.objects.filter(voterID=overflow_voter).exists())

    def test_vote_positions_enforced(self):
        wrong_mode_voter = self._create_user("voter-pos-wrong")
        res = self._post_vote(
            wrong_mode_voter,
            self.position_election,
            {"atLarge": [self.position_cand1.id]},
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["code"], "WRONG_MODE")

        overflow_voter = self._create_user("voter-pos-overflow")
        res = self._post_vote(
            overflow_voter,
            self.position_election,
            {
                "positions": [
                    {"candidacyId": self.position_cand1.id, "positionId": self.position_one.id},
                    {"candidacyId": self.position_cand2.id, "positionId": self.position_one.id},
                ]
            },
        )
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data["code"], "TOO_MANY_FOR_POSITION")
        self.assertEqual(data["position_id"], self.position_one.id)
        self.assertEqual(data["allowed"], 1)

        valid_voter = self._create_user("voter-pos-valid")
        res = self._post_vote(
            valid_voter,
            self.position_election,
            {
                "positions": [
                    {"candidacyId": self.position_cand1.id, "positionId": self.position_one.id},
                    {"candidacyId": self.position_cand3.id, "positionId": self.position_two.id},
                ]
            },
        )
        self.assertEqual(res.status_code, 200)
        vote = Vote.objects.get(voterID=valid_voter, election=self.position_election)
        self.assertEqual(
            set(vote.candidateID.values_list("id", flat=True)),
            {self.position_cand1.id, self.position_cand3.id},
        )
