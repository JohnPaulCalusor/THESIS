from datetime import date

from django.urls import reverse
from rest_framework.test import APIClient
from django.test import TestCase

from ..models import Election, Candidacy, User
from ..models_position import Position


class BallotCredentialsTest(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="pass1234",
            mobileNum="09171234567",
            region="Region",
            address="Addr",
            occupation="Student",
        )
        self.candidate_user = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            password="pass1234",
            mobileNum="09179876543",
            region="Region",
            address="Addr",
            occupation="Student",
        )
        self.election = Election.objects.create(
            title="Test Election",
            startDate=date(2025, 1, 1),
            endDate=date(2025, 1, 2),
            electionStatus=True,
        )
        self.position = Position.objects.create(election=self.election, title="Demo", sort=1)
        Candidacy.objects.create(
            candidate=self.candidate_user,
            election=self.election,
            position=self.position,
            credentials="Experienced leader",
        )

    def test_ballot_includes_credentials_for_member(self):
        client = APIClient()
        client.force_authenticate(self.member)
        url = reverse("election-ballot", kwargs={"election_id": self.election.id})
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("positions", body)
        first_pos = body["positions"][0]
        option = first_pos["options"][0]
        self.assertEqual(option["candidacyId"], Candidacy.objects.first().id)
        self.assertEqual(option["credentials"], "Experienced leader")
