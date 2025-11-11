import json
import secrets
import pytest
from uuid import uuid4
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APIClient
try:
    from rest_framework_simplejwt.tokens import RefreshToken
except Exception:  # pragma: no cover
    RefreshToken = None

User = get_user_model()


class TestEmailOtpApi:
    def setup_method(self):
        uid = uuid4().hex[:8]
        self.user = User.objects.create_user(
            username=f"otp-{uid}",
            email=f"otp+{uid}@example.com",
            password="strong-password",
            is_active=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @pytest.mark.django_db(transaction=True)
    def test_start_and_verify_happy_path(self, monkeypatch):
        monkeypatch.setattr(secrets, "randbelow", lambda n: 123456)
        start = self.client.post("/api/auth/email/start")
        assert start.status_code == 202
        assert "expires_at" in start.data

        verify = self.client.post("/api/auth/email/verify", {"code": "123456"})
        assert verify.status_code == 200
        self.user.refresh_from_db()
        assert self.user.email_verified

    @pytest.mark.django_db(transaction=True)
    def test_throttle_on_quick_resend(self, monkeypatch):
        monkeypatch.setattr(secrets, "randbelow", lambda n: 111111)
        self.client.post("/api/auth/email/start")
        throttled = self.client.post("/api/auth/email/start")
        assert throttled.status_code == 429
        assert throttled.data["code"] == "TOO_MANY_REQUESTS"
        assert throttled.data["message"] == "Please wait before requesting a new code."
        assert throttled.data["retry_after"] >= 0

    @pytest.mark.django_db(transaction=True)
    def test_verify_lockout_after_max_attempts(self, monkeypatch):
        monkeypatch.setattr(secrets, "randbelow", lambda n: 222222)
        self.client.post("/api/auth/email/start")
        resp = None
        for _ in range(settings.EMAIL_OTP_MAX_ATTEMPTS):
            resp = self.client.post("/api/auth/email/verify", {"code": "000000"})
        assert resp.status_code == 429
        assert resp.data["code"] == "TOO_MANY_ATTEMPTS"
        assert resp.data["message"] == "Please request a new code later."
        assert resp.data["retry_after"] >= 0
