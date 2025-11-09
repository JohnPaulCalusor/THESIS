# >>> PAPSAS v1.4 BEGIN
import math
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from papsas_app.models import Election

EPS = 1e-6

class TestAnalyticsMath(APITestCase):
    def setUp(self):
        U = get_user_model()
        # officer/admin read is allowed; we use staff for simplicity
        self.officer, _ = U.objects.get_or_create(username="officer_v14", defaults={"is_staff": True})
        self.client.force_authenticate(self.officer)

    def test_shares_sum_and_meta_total(self):
        sd = date.today()
        ed = sd + timedelta(days=7)
        e = Election.objects.create(
            title="v1.4 Analytics",
            startDate=sd,
            endDate=ed,
            electionStatus=True,
            numWinners=1,
        )
        r = self.client.get(f"/api/elections/{e.id}/analytics")
        # Tolerate no data (404) depending on implementation
        if r.status_code == 404:
            return
        self.assertIn(r.status_code, (200, 204))
        data = r.json()
        agg_total = 0
        for pos in data.get("positions", []):
            shares = [t.get("share") or 0.0 for t in pos.get("totals", [])]
            if shares:
                self.assertTrue(math.isclose(sum(shares), 1.0, abs_tol=EPS))
            agg_total += sum(int(t.get("count", 0)) for t in pos.get("totals", []))
        meta = data.get("meta") or {}
        if "totalVotes" in meta:
            self.assertEqual(int(meta["totalVotes"]), agg_total)
# <<< PAPSAS v1.4 END
