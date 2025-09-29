# papsas_app/tests/test_voting_rules.py
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from papsas_app.models import Election, Candidacy, Vote

User = get_user_model()

class VotingRulesTests(TestCase):
    def setUp(self):
        self.voter = User.objects.create_user(
            username="voter",
            email="voter@test.com",
            password="Pass1234!"
        )
        # Open election
        self.elec = Election.objects.create(
            title="Gen",
            startDate=timezone.now() - timezone.timedelta(days=1),
            endDate=timezone.now() + timezone.timedelta(days=1),
            electionStatus=True,
        )
        # Candidates
        self.c1 = Candidacy.objects.create(
            candidate=User.objects.create_user(username="c1", email="c1@test.com", password="x"),
            election=self.elec,
            candidacyStatus=True,
        )
        self.c2 = Candidacy.objects.create(
            candidate=User.objects.create_user(username="c2", email="c2@test.com", password="x"),
            election=self.elec,
            candidacyStatus=True,
        )

    def test_unique_vote_per_election_db_constraint(self):
        v1 = Vote.objects.create(voterID=self.voter, election=self.elec)
        v1.candidateID.set([self.c1.id])
        with self.assertRaises(Exception):
            Vote.objects.create(voterID=self.voter, election=self.elec)

    def test_election_summary_json_requires_login(self):
        url = reverse("election_summary_json")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)  # redirect to login

    def test_export_results_csv_staff_only(self):
        self.voter.is_staff = True
        self.voter.save()
        self.client.force_login(self.voter)
        url = reverse("export_results_csv", args=[self.elec.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/csv", resp["Content-Type"])
