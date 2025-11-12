import pytest
from uuid import uuid4
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.apps import apps
from rest_framework.test import APIClient

User = get_user_model()
Election = apps.get_model("papsas_app", "Election")

@pytest.fixture
def admin_user(db):
    u = User.objects.create_user(
        username=f"admin-{uuid4().hex[:6]}",
        email=f"admin+{uuid4().hex[:6]}@test.local",
        password="x",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    return u

@pytest.fixture
def officer_user(db):
    U = get_user_model()
    uid = uuid4().hex[:6]
    u = U.objects.create_user(
        username=f"officer+{uid}",
        email=f"officer+{uid}@test.local",
        password="x",
        is_staff=False,
    )
    # Ensure 'officer' group exists and user is a member (perm check uses group)
    from django.contrib.auth.models import Group

    g, _ = Group.objects.get_or_create(name="officer")
    u.groups.add(g)
    return u

@pytest.fixture
def member_user(db):
    """Plain authenticated member (no staff, no officer)."""
    U = get_user_model()
    uid = uuid4().hex[:6]
    return U.objects.create_user(
        username=f"member+{uid}",
        email=f"member+{uid}@test.local",
        password="x",
        is_staff=False,
    )

@pytest.fixture
def sample_election(db):
    return Election.objects.create(
        title=f"Sample {uuid4().hex[:4]}",
        startDate=date.today(),
        endDate=date.today() + timedelta(days=7),
        electionStatus=True,
        numWinners=1,
    )

@pytest.fixture
def api_client():
    return APIClient()
