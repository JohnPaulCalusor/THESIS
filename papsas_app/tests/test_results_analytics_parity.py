from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from papsas_app.models import Election, Candidacy

User = get_user_model()


class TestResultsAnalyticsParity(APITestCase):
    def setUp(self):
        today = date.today()
        self.officer, _ = User.objects.get_or_create(
            username="officer-parity",
            defaults={
                "email": "officer-parity@test.local",
                "is_staff": True,
                "is_active": True,
            },
        )
        self.voter_one = User.objects.create_user(
            username="parity-voter-one",
            email="parity-voter-one@test.local",
            password="password",
            is_active=True,
        )
        self.voter_two = User.objects.create_user(
            username="parity-voter-two",
            email="parity-voter-two@test.local",
            password="password",
            is_active=True,
        )

        self.election = Election.objects.create(
            title="Parity Election",
            startDate=today,
            endDate=today,
            electionStatus=True,
            numWinners=1,
        )

        self.candidate_one = User.objects.create_user(
            username="parity-candidate-one",
            email="parity-candidate-one@test.local",
            password="password",
            is_active=True,
        )
        self.candidate_two = User.objects.create_user(
            username="parity-candidate-two",
            email="parity-candidate-two@test.local",
            password="password",
            is_active=True,
        )

        self.candidacy_one = Candidacy.objects.create(
            election=self.election,
            candidate=self.candidate_one,
            candidacyStatus=True,
        )
        self.candidacy_two = Candidacy.objects.create(
            election=self.election,
            candidate=self.candidate_two,
            candidacyStatus=True,
        )

        self._cast_vote(self.voter_one, self.candidacy_one)
        self._cast_vote(self.voter_two, self.candidacy_two)

    def _cast_vote(self, voter, candidacy):
        self.client.force_authenticate(voter)
        payload = {"atLarge": [candidacy.id]}
        resp = self.client.post(f"/api/elections/{self.election.id}/vote", payload, format="json")
        self.assertEqual(resp.status_code, 200, resp.content)

    def _flatten_counts(self, payload):
        out = {}
        for position in payload.get("positions", []):
            for total in position.get("totals", []):
                cid = total.get("candidate_id")
                if cid is None:
                    continue
                out[cid] = int(total.get("count", 0))
        return out

    def test_results_and_analytics_share_totals(self):
        self.client.force_authenticate(self.officer)
        results = self.client.get(f"/api/elections/{self.election.id}/results")
        analytics = self.client.get(f"/api/elections/{self.election.id}/analytics")
        self.assertEqual(results.status_code, 200)
        self.assertEqual(analytics.status_code, 200)

        results_data = results.json()
        analytics_data = analytics.json()

        results_total = sum(self._flatten_counts(results_data).values())
        analytics_totals = self._flatten_counts(analytics_data)
        analytics_total = sum(analytics_totals.values())

        self.assertEqual(results_total, analytics_total)
        if "total_votes" in analytics_data:
            self.assertEqual(analytics_data["total_votes"], analytics_total)

        self.assertEqual(
            self._flatten_counts(results_data),
            self._flatten_counts(analytics_data),
        )
