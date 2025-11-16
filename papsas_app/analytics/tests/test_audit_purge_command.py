from io import StringIO
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from papsas_app.analytics.models import AuditEvent


class AuditPurgeCommandTests(TestCase):
    def test_audit_purge_dry_run_and_execution(self):
        now = timezone.now()
        old = AuditEvent.objects.create(
            actor_username="old",
            action="OLD",
            target_type="audit",
            target_id="1",
        )
        recent = AuditEvent.objects.create(
            actor_username="new",
            action="NEW",
            target_type="audit",
            target_id="2",
        )
        AuditEvent.objects.filter(pk=old.pk).update(ts=now - timezone.timedelta(days=10))
        AuditEvent.objects.filter(pk=recent.pk).update(ts=now - timezone.timedelta(days=1))

        with override_settings(AUDIT_RETENTION_DAYS=5):
            buf = StringIO()
            call_command("audit_purge", "--dry-run", stdout=buf)
            self.assertIn("Would delete 1 audit events", buf.getvalue())
            self.assertEqual(AuditEvent.objects.count(), 2)

            buf = StringIO()
            call_command("audit_purge", stdout=buf)
            self.assertIn("Deleted 1 audit events", buf.getvalue())

        remaining = AuditEvent.objects.all()
        self.assertEqual(remaining.count(), 1)
        self.assertEqual(remaining.first().id, recent.id)
