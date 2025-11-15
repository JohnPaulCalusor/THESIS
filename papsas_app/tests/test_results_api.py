from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.apps import apps


class ResultsApiTest(TestCase):
    def setUp(self):
        label = "papsas_app"
        self.User = get_user_model()
        self.Election = apps.get_model(label, "Election")
        self.Position = apps.get_model(label, "Position")
        self.Candidacy = apps.get_model(label, "Candidacy")
        self.Vote = apps.get_model(label, "Vote")

        self.u1 = self.User.objects.create_user(username="u1", password="x", email="u1@example.com")
        self.u2 = self.User.objects.create_user(username="u2", password="x", email="u2@example.com")

        self.e = self.Election.objects.create(
            title="T",
            startDate="2025-11-01",
            endDate="2025-11-08",
            electionStatus=True,
            numWinners=1,
        )
        self.p_ad = self.Position.objects.create(
            election=self.e,
            title="Advisers",
            enabled=True,
            sort=1,
        )
        self.p_dir = self.Position.objects.create(
            election=self.e,
            title="Director",
            enabled=True,
            sort=2,
        )

        self.c_alice = self.Candidacy.objects.create(
            election=self.e,
            position=self.p_ad,
            candidacyStatus=True,
            credentials="",
            candidate=self.u1,
        )
        self.c_bob = self.Candidacy.objects.create(
            election=self.e,
            position=self.p_dir,
            candidacyStatus=True,
            credentials="",
            candidate=self.u2,
        )

        # create votes: u1 votes for alice; u2 votes for alice + bob
        v1 = self.Vote.objects.create(
            voterID=self.u1,
            election=self.e,
            voteDate="2025-11-05",
        )
        v1.candidateID.add(self.c_alice)

        v2 = self.Vote.objects.create(
            voterID=self.u2,
            election=self.e,
            voteDate="2025-11-05",
        )
        v2.candidateID.add(self.c_alice, self.c_bob)

    def test_results_counts(self):
        url = reverse("election-results", args=[self.e.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["election"]["id"], self.e.id)

        advisers = next(p for p in data["positions"] if p["title"] == "Advisers")
        alice_row = next(t for t in advisers["totals"] if t["candidate_id"] == self.u1.id)
        self.assertEqual(alice_row["count"], 2)

        director = next(p for p in data["positions"] if p["title"] == "Director")
        bob_row = next(t for t in director["totals"] if t["candidate_id"] == self.u2.id)
        self.assertEqual(bob_row["count"], 1)
