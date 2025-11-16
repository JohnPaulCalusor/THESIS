from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import AuditEvent


class Command(BaseCommand):
    help = "Purge audit events older than the configured retention window."

    def add_arguments(self, parser):
        parser.add_argument("--older-than", type=int, help="Days to keep; overrides AUDIT_RETENTION_DAYS.")
        parser.add_argument("--dry-run", action="store_true", help="Show how many rows would be deleted without touching the database.")

    def handle(self, *args, **options):
        days = options["older_than"] if options["older_than"] is not None else getattr(settings, "AUDIT_RETENTION_DAYS", 180)
        cutoff = timezone.now() - timezone.timedelta(days=days)
        qs = AuditEvent.objects.filter(ts__lt=cutoff)
        count = qs.count()
        if options["dry_run"]:
            self.stdout.write(f"[DRY RUN] Would delete {count} audit events older than {cutoff.isoformat()}")
            return
        deleted, _ = qs.delete()
        self.stdout.write(f"Deleted {count} audit events older than {cutoff.isoformat()}")
