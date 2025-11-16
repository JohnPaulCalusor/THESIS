from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from papsas_app.analytics.models import AuditEvent

User = get_user_model()


class AuditApiPermsTests(TestCase):
    def _ensure_groups(self):
        admin_group, _ = Group.objects.get_or_create(name="admin")
        officer_group, _ = Group.objects.get_or_create(name="officer")
        return admin_group, officer_group

    def _create_user(self, username, group):
        user, _ = User.objects.get_or_create(username=username, defaults={"email": f"{username}@test.local"})
        user.set_password("password")
        user.save()
        user.groups.add(group)
        return user

    def test_admin_access_and_officer_denied(self):
        admin_group, officer_group = self._ensure_groups()
        admin = self._create_user("audit-admin", admin_group)
        officer = self._create_user("audit-officer", officer_group)

        AuditEvent.objects.create(actor=admin, actor_username=admin.username, action="TEST", target_type="audit", target_id="1")

        client = APIClient()
        client.force_authenticate(admin)
        r = client.get("/api/audit/events")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(r.data["count"], 1)

        client.force_authenticate(officer)
        r = client.get("/api/audit/events")
        self.assertEqual(r.status_code, 403)
