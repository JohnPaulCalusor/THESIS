from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestAuthLogin(APITestCase):
    """
    Regression test for /api/auth/login (EmailTokenObtainPairView).

    This test is defensive: it creates a user, ensures they are active and
    "verified" (if such flags exist), then tries both email-based and
    username-based payloads. It passes as soon as any payload returns 200
    with {access, refresh} JWTs.
    """

    def setUp(self):
        User = get_user_model()
        self.password = "LoginTest123!"
        self.email = "login-test@example.com"

        # Create a user compatible with the custom User model
        # Try email-only first (common for USERNAME_FIELD = "email"),
        # then fall back to username+email if required.
        try:
            self.user = User.objects.create_user(
                email=self.email,
                password=self.password,
            )
        except TypeError:
            # Fallback if the user model still expects a username
            self.user = User.objects.create_user(
                username="login-test-user",
                email=self.email,
                password=self.password,
            )

        # Make sure the user is active and, if applicable, marked as verified
        if hasattr(self.user, "is_active"):
            self.user.is_active = True

        for attr in ("is_verified", "email_verified", "is_email_verified"):
            if hasattr(self.user, attr):
                setattr(self.user, attr, True)

        self.user.save()

        # Resolve the login URL: prefer the named route, fallback to raw path
        try:
            self.login_url = reverse("token_obtain_pair")
        except Exception:
            self.login_url = "/api/auth/login"

    def test_auth_login_returns_jwt_tokens(self):
        # Try logging in with email and/or username depending on what exists
        payloads = []

        if getattr(self.user, "email", None):
            payloads.append({"email": self.user.email, "password": self.password})

        if hasattr(self.user, "username") and getattr(self.user, "username", None):
            payloads.append({"username": self.user.username, "password": self.password})

        last_response = None

        for payload in payloads:
            last_response = self.client.post(self.login_url, payload, format="json")

            if last_response.status_code == status.HTTP_200_OK:
                data = last_response.json()
                self.assertIn("access", data)
                self.assertIn("refresh", data)
                self.assertIsInstance(data["access"], str)
                self.assertIsInstance(data["refresh"], str)
                return  # success → stop the test

        # If we get here, no payload succeeded
        status_code = getattr(last_response, "status_code", None)
        content = getattr(last_response, "content", b"")
        self.fail(
            f"Login did not succeed with any tested credential payloads; "
            f"last status {status_code}, body={content!r}"
        )
