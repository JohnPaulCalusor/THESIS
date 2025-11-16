from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.test import RequestFactory, TransactionTestCase

from ..audit import _safe_hash, log_event, scrub_payload
from ..models import AuditEvent


class AuditWriterTests(TransactionTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_log_event_uses_on_commit(self):
        request = self.factory.get("/audit")
        request.user = AnonymousUser()
        request.META["REMOTE_ADDR"] = "127.0.0.1"
        request.META["HTTP_USER_AGENT"] = "pytest"

        with transaction.atomic():
            log_event(
                request,
                action="audit.test",
                target_type="test",
                target_id="42",
            )
            self.assertEqual(AuditEvent.objects.count(), 0)

        after = AuditEvent.objects.get()
        self.assertEqual(after.action, "audit.test")
        self.assertEqual(after.target_type, "test")

    def test_scrub_payload_and_hash(self):
        payload = {
            "password": "secret",
            "refresh": "token",
            "nested": {"otp": "123456", "safe": "ok"},
        }
        scrubbed = scrub_payload(payload)
        self.assertEqual(scrubbed["password"], "***")
        self.assertEqual(scrubbed["refresh"], "***")
        self.assertEqual(scrubbed["nested"]["otp"], "***")
        self.assertEqual(scrubbed["nested"]["safe"], "ok")

        hashed = _safe_hash(payload)
        self.assertEqual(len(hashed), 64)
        int(hashed, 16)  # ensure hex digest
