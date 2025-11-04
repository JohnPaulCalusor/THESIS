# papsas_app/tests/test_rbac_candidacies.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework.test import APIClient

from papsas_app.models import Election, Position

class TestCandidacyRBAC(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        # Ensure groups exist
        cls.g_admin, _ = Group.objects.get_or_create(name="admin")
        cls.g_officer, _ = Group.objects.get_or_create(name="officer")

        # Users
        cls.admin = User.objects.create_user(
            username="admin@test.local", email="admin@test.local", password="adminpass"
        )
        cls.admin.is_staff = True
        cls.admin.save(update_fields=["is_staff"])
        cls.admin.groups.add(cls.g_admin)

        cls.officer = User.objects.create_user(
            username="officer@test.local", email="officer@test.local", password="officerpass"
        )
        cls.officer.groups.add(cls.g_officer)

        # Minimal election + position
        today = timezone.now().date()
        cls.election = Election.objects.create(
            title="RBAC Test Election",
            startDate=today,
            endDate=today,
            electionStatus=True,
            numWinners=1,
        )
        cls.position = Position.objects.create(
            election=cls.election,
            title="Advisers",
        )

    def setUp(self):
        self.client = APIClient()

    def test_officer_can_read_but_cannot_write(self):
        self.client.force_authenticate(user=self.officer)

        url = f"/api/elections/{self.election.id}/candidacies"

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200, f"GET as officer should be 200, got {r.status_code}")

        payload = {"email": "candidate1@test.local", "name": "Candidate One", "position_id": self.position.id}
        r = self.client.post(url, payload, format="json")
        self.assertEqual(r.status_code, 403, f"POST as officer should be 403, got {r.status_code}")

    def test_admin_can_read_and_write(self):
        self.client.force_authenticate(user=self.admin)

        url = f"/api/elections/{self.election.id}/candidacies"

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200, f"GET as admin should be 200, got {r.status_code}")

        payload = {"email": "candidate2@test.local", "name": "Candidate Two", "position_id": self.position.id}
        r = self.client.post(url, payload, format="json")
        self.assertIn(r.status_code, (200, 201), f"POST as admin should be 200/201, got {r.status_code}")
        self.assertIn("id", r.data)
