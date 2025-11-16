from datetime import timedelta, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from papsas_app.models import Event, Venue


class EventsApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="event-owner",
            email="owner@example.com",
            password="secret123",
        )
        self.venue = Venue.objects.create(
            name="Main Hall",
            address="123 Main St",
            capacity=250,
        )
        image = SimpleUploadedFile("pubmat.png", b"content", content_type="image/png")
        now = timezone.now().date()
        self.event = Event.objects.create(
            eventName="Launch Gala",
            exclusive=False,
            startDate=now,
            endDate=now + timedelta(days=1),
            venue=self.venue,
            eventDescription="Join us for the launch.",
            eventStatus=True,
            price=Decimal("12.00"),
            startTime=time(9, 0),
            endTime=time(12, 0),
            pubmat=image,
            created_by=self.user,
        )

    def test_events_list_returns_canonical_fields(self):
        client = APIClient()
        response = client.get("/api/events")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data)
        event_obj = next(item for item in data if item["slug"] == self.event.slug)
        self.assertEqual(event_obj["title"], "Launch Gala")
        self.assertEqual(event_obj["status"], "published")
        self.assertEqual(event_obj["created_by"]["id"], self.user.id)
        self.assertIn("starts_at", event_obj)

    def test_event_detail_by_slug(self):
        client = APIClient()
        response = client.get(f"/api/events/{self.event.slug}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["slug"], self.event.slug)

    def test_events_ics_includes_events(self):
        client = APIClient()
        response = client.get("/api/events.ics")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/calendar; charset=utf-8")
        content = response.content.decode("utf-8")
        self.assertIn("BEGIN:VCALENDAR", content)
        self.assertIn(f"SUMMARY:{self.event.eventName}", content)
        self.assertIn(f"UID:event-{self.event.id}", content)
