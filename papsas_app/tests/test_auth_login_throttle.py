from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class TestAuthLoginThrottle(APITestCase):
    """
    Ensure /api/auth/login enforces the auth_login throttle scope
    and returns the expected error shape when rate limited.
    """

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="u1",
            email="u1@example.com",
            password="p1",
            is_active=True,
        )
        self.url = "/api/auth/login"

    def test_auth_login_throttles_after_limit(self):
        original_rate = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].get("auth_login")
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["auth_login"] = "3/minute"
        allowed_hosts = list(settings.ALLOWED_HOSTS) + ["testserver"]

        try:
            with override_settings(ALLOWED_HOSTS=allowed_hosts):
                client = APIClient()
                cache.clear()
                payload = {"username": self.user.username, "password": "wrong"}
                attempts = []
                for _ in range(8):
                    attempts.append(client.post(self.url, payload, format="json"))

                throttled = [
                    attempt for attempt in attempts
                    if attempt.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                ]
                self.assertTrue(throttled, "Expected at least one throttled response")
                data = throttled[0].json()
                self.assertEqual(data.get("code"), "RATE_LIMITED")
                self.assertIsInstance(data.get("message"), str)
                self.assertTrue(data.get("message"))
                self.assertIn("retry_after", data)
        finally:
            if original_rate is None:
                settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].pop("auth_login", None)
            else:
                settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["auth_login"] = original_rate
