# pytest or Django test runner compatible
# Verifies RBAC on /api/elections/:id/candidacies
# Officer/Admin can READ; only Admin can WRITE (create).
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# If your models live elsewhere, adjust these imports:
from papsas_app.models import Election, Position
from rest_framework_simplejwt.tokens import RefreshToken


def bearer_for(user):
    access = RefreshToken.for_user(user).access_token
    return f"Bearer {access}"


class TestCandidacyRBAC(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        # Ensure groups exist
        cls.g_admin, _ = Group.objects.get_or_create(name="admin")
        cls.g_officer, _ = Group.objects.get_or_create(name="officer")

        # Create users
        cls.admin = User.objects.create_user(
            username="admin@test.local", email="admin@test.local", password="adminpass"
        )
        cls.admin.is_staff = True  # your RBAC accepts is_staff OR group 'admin'
        cls.admin.save(update_fields=["is_staff"])
        cls.admin.groups.add(cls.g_admin)

        cls.officer = User.objects.create_user(
            username="officer@test.local", email="officer@test.local", password="officerpass"
        )
        cls.officer.groups.add(cls.g_officer)

        # Minimal election + position so GET/POST have valid targets
        today = timezone.now().date()
        cls.election = Election.objects.create(
            title="RBAC Test Election",
            start_date=today,
            end_date=today,          # adjust if your model requires future end
            election_status=True,    # adjust field name if different
            num_winners=1,           # adjust if your model differs
        )
        cls.position = Position.objects.create(
            election=cls.election, title="Advisers", enabled=True, sort=1
        )

        cls.base_url = f"/api/elections/{cls.election.id}/candidacies"

    def test_officer_can_read_but_cannot_write(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=bearer_for(self.officer))

        # READ should be allowed
        r_get = client.get(self.base_url)
        assert r_get.status_code == status.HTTP_200_OK

        # WRITE should be forbidden
        r_post = client.post(
            self.base_url,
            {"email": "officer-create@test.local", "name": "Officer Try", "position_id": self.position.id},
            format="json",
        )
        assert r_post.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_read_and_write(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=bearer_for(self.admin))

        # READ should be allowed
        r_get = client.get(self.base_url)
        assert r_get.status_code == status.HTTP_200_OK

        # WRITE should be allowed
        payload = {
            "email": "admin-create@test.local",
            "name": "Admin Created",
            "position_id": self.position.id,
        }
        r_post = client.post(self.base_url, payload, format="json")
        assert r_post.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        data = r_post.json()
        # Basic sanity checks on response shape
        assert "id" in data
        assert data.get("candidate", {}).get("email") == payload["email"]
        assert data.get("position", {}).get("id") == self.position.id
