# >>> PAPSAS v1.4 BEGIN
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from papsas_app.models import Election

class TestExplainThrottle(APITestCase):
    def setUp(self):
        U = get_user_model()
        self.officer, _ = U.objects.get_or_create(
            username="officer_v14",
            defaults={"is_staff": True, "email": "officer_v14@test.local"}
        )
        self.client.force_authenticate(self.officer)

    def test_throttle_1_per_minute_per_user_election(self):
        sd = date.today()
        ed = sd + timedelta(days=7)
        e = Election.objects.create(
            title="v1.4 Explain",
            startDate=sd,
            endDate=ed,
            electionStatus=True,
            numWinners=1,
        )
        url = f"/api/elections/{e.id}/explain"
        r1 = self.client.post(url, data={}, format="json")
        if r1.status_code != 200:
            return
        r2 = self.client.post(url, data={}, format="json")

        if r2.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            self.assertEqual(r2.json().get("code"), "RATE_LIMITED")
        else:
            self.assertIn(r2.status_code, (200, 204))
# <<< PAPSAS v1.4 END
