import secrets

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from papsas_app.models import User


@pytest.mark.django_db
class TestEmailOtpFlow:
    def setup_method(self):
        self.user = User.objects.create_user(
            username="test",
            email="test@example.com",
            password="strongpwd",
            is_active=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_start_happy_path(self, monkeypatch):
        monkeypatch.setattr(secrets, "randbelow", lambda n: 123456)
        response = self.client.post("/api/auth/email/start")
        assert response.status_code == 202
        assert response.data.get("expires_at")

    def test_start_throttled(self):
        self.client.post("/api/auth/email/start")
        throttled = self.client.post("/api/auth/email/start")
        assert throttled.status_code == 429
        assert "retry_after" in throttled.data

    def test_verify_happy_path(self, monkeypatch):
        monkeypatch.setattr(secrets, "randbelow", lambda n: 123456)
        self.client.post("/api/auth/email/start")
        response = self.client.post("/api/auth/email/verify", {"code": "123456"})
        assert response.status_code == 200
        self.user.refresh_from_db()
        assert self.user.email_verified

    def test_verify_max_attempts_locks(self, monkeypatch):
        monkeypatch.setattr(secrets, "randbelow", lambda n: 123456)
        self.client.post("/api/auth/email/start")
        response = None
        for _ in range(settings.EMAIL_OTP_MAX_ATTEMPTS):
            response = self.client.post("/api/auth/email/verify", {"code": "000000"})
        assert response.status_code == 429
        locked_response = self.client.post("/api/auth/email/verify", {"code": "000000"})
        assert locked_response.status_code == 429

    def test_me_patch_triggers_new_otp(self, monkeypatch):
        monkeypatch.setattr(secrets, "randbelow", lambda n: 654321)
        response = self.client.patch("/api/me", {"email": "new@example.com"})
        assert response.status_code == 200
        assert response.data.get("otp_expires_at")
        self.user.refresh_from_db()
        assert not self.user.email_verified

    def test_admin_endpoint_requires_email_verified(self):
        admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="strongpwd",
            is_staff=True,
            email_verified=False,
        )
        client = APIClient()
        client.force_authenticate(admin)
        assert client.get("/api/users").status_code == 403
