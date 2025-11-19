from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from papsas_app.api.views import AUTHENTICATION_FAILED_MESSAGE


class TestAuthLogin(APITestCase):
    """
    Regression tests for /api/auth/login (EmailTokenObtainPairView).

    These tests are defensive: they create a user, ensure they are active and
    verified (if such flags exist), and then exercise the username field as
    either a username or an email identifier. We also assert an unknown
    identifier returns the expected AUTHENTICATION_FAILED error.
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

    def _login_with_identifier(self, identifier):
        return self.client.post(
            self.login_url,
            {"username": identifier, "password": self.password},
            format="json",
        )

    def _assert_jwt_response(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertIsInstance(data["access"], str)
        self.assertIsInstance(data["refresh"], str)

    def test_auth_login_returns_jwt_tokens_with_username(self):
        response = self._login_with_identifier(self.user.username)
        self._assert_jwt_response(response)

    def test_auth_login_returns_jwt_tokens_with_email_identifier(self):
        response = self._login_with_identifier(self.user.email)
        self._assert_jwt_response(response)

    def test_auth_login_returns_authentication_failed_for_unknown_identifier(self):
        response = self._login_with_identifier("unknown-identifier@example.com")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json(),
            {
                "code": "AUTHENTICATION_FAILED",
                "message": AUTHENTICATION_FAILED_MESSAGE,
            },
        )

