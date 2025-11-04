# >>> PAPSAS v1.4 BEGIN
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from papsas_app.models import Election, Position, Candidacy

class TestCandidacyDuplicateGuard(APITestCase):
    def setUp(self):
        U = get_user_model()
        self.admin, _ = U.objects.get_or_create(
            username="admin_v14",
            defaults={"is_staff": True, "email": "admin_v14@test.local"}
        )
        # ensure staff even if it pre-existed
        if not self.admin.is_staff:
            self.admin.is_staff = True
            self.admin.save(update_fields=["is_staff"])
        self.client.force_authenticate(self.admin)

    def test_duplicate_candidacy_returns_409(self):
        sd = date.today()
        ed = sd + timedelta(days=7)
        e = Election.objects.create(
            title="v1.4 Elex",
            startDate=sd,
            endDate=ed,
            electionStatus=True,
            numWinners=1,
        )
        # Position must belong to an election
        p = Position.objects.create(title="Chair", election=e)
        U = get_user_model()
        cand = U.objects.create(username="cand_v14", email="cand_v14@test.local")

        # First record via ORM to avoid serializer differences
        Candidacy.objects.create(election=e, position=p, candidate=cand)

        # Duplicate via API
        url = f"/api/elections/{e.id}/candidacies"
        r = self.client.post(url, data={"candidate_id": cand.id, "position_id": p.id}, format="json")

        # Accept 409 or 400 (serializer-level dupe); assert code on 409
        self.assertIn(r.status_code, (status.HTTP_409_CONFLICT, status.HTTP_400_BAD_REQUEST))
        if r.status_code == status.HTTP_409_CONFLICT:
            self.assertEqual(r.json().get("code"), "ALREADY_EXISTS")
# <<< PAPSAS v1.4 END
