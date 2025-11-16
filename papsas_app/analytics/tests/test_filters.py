from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.test import APIClient

from papsas_app.analytics.models import AuditEvent

User = get_user_model()


class AuditFiltersTests(TestCase):
    def _setup_admin(self):
        group, _ = Group.objects.get_or_create(name="admin")
        user, _ = User.objects.get_or_create(username="filter-admin", defaults={"email": "filter-admin@test.local"})
        user.groups.add(group)
        user.set_password("password")
        user.save()
        return user

    def _aware_from_iso(self, value: str):
        dt = parse_datetime(value)
        if dt is None:
            return None
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.utc)
        return dt

    def test_filters_by_action_and_election_and_time(self):
        admin = self._setup_admin()
        now = timezone.now()
        old = now - timedelta(days=2)
        recent = now - timedelta(hours=1)
        AuditEvent.objects.create(
            actor=admin,
            actor_username=admin.username,
            action="AUTH_LOGIN_SUCCESS",
            scope_election_id=2,
            ts=old,
            target_type="auth",
            target_id="login",
        )
        AuditEvent.objects.create(
            actor=admin,
            actor_username=admin.username,
            action="VOTE_SUBMITTED",
            scope_election_id=1,
            ts=recent,
            target_type="vote",
            target_id="vote1",
        )
        AuditEvent.objects.create(
            actor=admin,
            actor_username=admin.username,
            action="VOTE_SUBMITTED",
            scope_election_id=1,
            ts=recent + timedelta(minutes=1),
            target_type="vote",
            target_id="vote2",
        )

        client = APIClient()
        client.force_authenticate(admin)

        r = client.get("/api/audit/events", {"action": "VOTE_SUBMITTED"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(all(row["action"] == "VOTE_SUBMITTED" for row in r.data["results"]))

        r = client.get("/api/audit/events", {"election": 1})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(all(row["scope_election_id"] == 1 for row in r.data["results"]))

        since = (now - timedelta(hours=2)).isoformat()
        r = client.get("/api/audit/events", {"since": since})
        self.assertEqual(r.status_code, 200)
        threshold = self._aware_from_iso(since)
        self.assertIsNotNone(threshold)
        results = [self._aware_from_iso(row["ts"]) for row in r.data["results"]]
        self.assertTrue(all(result and result >= threshold for result in results))
