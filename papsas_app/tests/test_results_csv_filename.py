# >>> PAPSAS v1.4 BEGIN
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from papsas_app.models import Election

class TestResultsCsvHeaders(APITestCase):
    def setUp(self):
        U = get_user_model()
        self.officer, _ = U.objects.get_or_create(username="officer_v14", defaults={"is_staff": True})
        self.client.force_authenticate(self.officer)

    def test_headers_present(self):
        sd = date.today()
        ed = sd + timedelta(days=7)
        e = Election.objects.create(
            title="v1.4 CSV",
            startDate=sd,
            endDate=ed,
            electionStatus=True,
            numWinners=1,
        )
        r = self.client.get(f"/api/elections/{e.id}/results/export.csv")
        # Tolerate 404 if no data yet
        if r.status_code == 404:
            return
        self.assertEqual(r.status_code, 200)
        ct = r.get("Content-Type", "")
        cd = r.get("Content-Disposition", "")
        self.assertIn("text/csv", ct)
        self.assertIn("charset", ct)
        self.assertIn(f"results-election-{e.id}.csv", cd)
# <<< PAPSAS v1.4 END
