from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from papsas_app.analytics.models import AuditEvent
from papsas_app.models import Event, EventSignup


class EventRegistrationAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="pw",
            is_active=True,
        )
        self.event = Event.objects.create(
            eventName="Annual Meetup",
            exclusive=True,
        )
        self.url = f"/api/events/{self.event.id}/registration"
        self.client.force_authenticate(user=self.user)

    def test_registration_lifecycle_updates_state_and_audit(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.json().get("registered"))

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.json().get("registered"))

        response = self.client.get(self.url)
        self.assertTrue(response.json().get("registered"))

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.url)
        self.assertFalse(response.json().get("registered"))

        created = AuditEvent.objects.filter(
            action="REGISTRATION_CREATED",
            meta__event_id=self.event.id,
            meta__user_id=self.user.id,
        ).last()
        self.assertIsNotNone(created)
        deleted = AuditEvent.objects.filter(
            action="REGISTRATION_DELETED",
            meta__event_id=self.event.id,
            meta__user_id=self.user.id,
        ).last()
        self.assertIsNotNone(deleted)

    def test_post_conflict_returns_already_registered_and_audit(self):
        EventSignup.objects.create(event=self.event, user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        payload = response.json()
        self.assertEqual(payload.get("code"), "ALREADY_REGISTERED")

        rejected = AuditEvent.objects.filter(
            action="REGISTRATION_REJECTED",
            meta__event_id=self.event.id,
            meta__user_id=self.user.id,
            meta__reason="already_registered",
        ).last()
        self.assertIsNotNone(rejected)

    def test_delete_conflict_returns_not_registered_and_audit(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        payload = response.json()
        self.assertEqual(payload.get("code"), "NOT_REGISTERED")

        rejected = AuditEvent.objects.filter(
            action="REGISTRATION_REJECTED",
            meta__event_id=self.event.id,
            meta__user_id=self.user.id,
            meta__reason="not_registered",
        ).last()
        self.assertIsNotNone(rejected)

    def test_throttle_enforces_rate_limit_and_logs_rejection(self):
        original_rate = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].get("event_register")
        settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["event_register"] = "3/minute"
        cache.clear()
        try:
            responses = []
            for _ in range(6):
                responses.append(self.client.post(self.url))
            throttled = [
                resp for resp in responses if resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            ]
            self.assertTrue(throttled, "Expected at least one throttled response")
            data = throttled[0].json()
            self.assertEqual(data.get("code"), "RATE_LIMITED")
            self.assertIn("retry_after", data)

            rejected = AuditEvent.objects.filter(
                action="REGISTRATION_REJECTED",
                meta__event_id=self.event.id,
                meta__user_id=self.user.id,
                meta__reason="throttled",
            ).last()
            self.assertIsNotNone(rejected)
        finally:
            if original_rate is None:
                settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].pop("event_register", None)
            else:
                settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["event_register"] = original_rate
