import json
from datetime import date, timedelta

from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from papsas_app.models import Election


def _ensure_election_pk1():
    # Create a minimal election with pk=1 if it doesn't exist yet.
    Election.objects.get_or_create(
        id=1,
        defaults=dict(
            title="Dev Election",
            startDate=date.today(),
            endDate=date.today() + timedelta(days=10),
            electionStatus=True,
            numWinners=None,
        ),
    )


def test_officer_cannot_create_candidacy(db):
    _ensure_election_pk1()

    U = get_user_model()
    officer, _ = U.objects.get_or_create(
        username="officer",
        defaults=dict(is_active=True, is_staff=False),
    )
    g, _ = Group.objects.get_or_create(name="officer")
    officer.groups.add(g)

    client = APIClient()
    client.force_authenticate(officer)
    resp = client.post(
        "/api/elections/1/candidacies",
        data=json.dumps({
            "email": "x@test.local",
            "name": "X",
            "positionId": 2,
            "credentials": "N/A",
            "status": True,
        }),
        content_type="application/json",
    )
    assert resp.status_code in (401, 403)


def test_admin_can_create_candidacy(db):
    _ensure_election_pk1()

    U = get_user_model()
    admin, _ = U.objects.get_or_create(
        username="admin",
        defaults=dict(is_active=True, is_staff=True),
    )
    g, _ = Group.objects.get_or_create(name="admin")
    admin.groups.add(g)

    client = APIClient()
    client.force_authenticate(admin)
    resp = client.post(
        "/api/elections/1/candidacies",
        data=json.dumps({
            "email": "y@test.local",
            "name": "Y",
            "positionId": 2,
            "credentials": "OK",
            "status": True,
        }),
        content_type="application/json",
    )
    assert resp.status_code in (200, 201)
