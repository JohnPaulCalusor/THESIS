import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "papsas.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

class AuthMeTests(TestCase):
    def test_auth_me_unauth_401(self):
        client = APIClient()
        r = client.get("/api/auth/me/")
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_me_returns_groups_and_fields(self):
        g, _ = Group.objects.get_or_create(name="officer")
        User = get_user_model()
        u = User.objects.create_user(
            username="alice", password="pass", email="a@x.tld",
            first_name="A", last_name="L", is_active=True
        )
        u.groups.add(g)
        client = APIClient()
        client.force_authenticate(user=u)
        r = client.get("/api/auth/me/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(data["username"], "alice")
        self.assertEqual(data["email"], "a@x.tld")
        self.assertIn("officer", data.get("groups", []))
