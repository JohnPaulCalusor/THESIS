import json
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model, models as auth_models
from rest_framework.test import APIClient
from papsas_app.models import Election, Candidacy

User = get_user_model()


def _ensure_position_with_optional_election(P, e):
    field_names = {f.name for f in P._meta.fields}
    params = {}
    if "title" in field_names:
        params["title"] = "President"
    elif "name" in field_names:
        params["name"] = "President"
    if "election" in field_names and e is not None:
        params["election"] = e
    p, _ = P.objects.get_or_create(**params)
    return p

def _has_pos_fk():
    for f in Candidacy._meta.get_fields():
        if getattr(f, "many_to_one", False):
            m = getattr(getattr(f, "remote_field", None), "model", None)
            if m and m is not User and f.name != "election":
                return f
    return None

def _admin_user():
    u,_ = User.objects.get_or_create(username="admin@test.local", defaults={"email":"admin@test.local"})
    u.set_password("adminpass123!"); u.is_staff=True; u.save()
    auth_models.Group.objects.get_or_create(name="admin")[0].user_set.add(u)
    return u

def _officer_user():
    u,_ = User.objects.get_or_create(username="officer@test.local", defaults={"email":"officer@test.local"})
    u.set_password("officerpass123!"); u.is_staff=False; u.save()
    auth_models.Group.objects.get_or_create(name="officer")[0].user_set.add(u)
    return u

def _token(u):
    from rest_framework_simplejwt.tokens import RefreshToken
    return str(RefreshToken.for_user(u).access_token)

def _current_election():
    today = timezone.now().date()
    e,_ = Election.objects.update_or_create(
        title="Test Election",
        defaults=dict(startDate=today, endDate=today, electionStatus=True, numWinners=1),
    )
    return e

def test_current_election_ok(db):
    client = APIClient()
    e = _current_election()
    r = client.get("/api/elections/current")
    assert r.status_code == 200
    assert r.json()["id"] == e.id

def test_admin_candidacy_create_list_patch_delete(db):
    client = APIClient()
    e = _current_election()
    admin = _admin_user()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {_token(admin)}")

    cand,_ = User.objects.get_or_create(username="cand@test.local", defaults={"email":"cand@test.local","first_name":"Juan","last_name":"Dela Cruz"})
    # API now expects either member_id or email+name; send member_id + optional position_id
    payload = {"member_id": cand.id, "credentials": "BSCS", "status": True}
    posf = _has_pos_fk()
    if posf:
        P = posf.remote_field.model
        p = _ensure_position_with_optional_election(P, e)
        payload["positionId"] = p.id

        r = client.post(
            f"/api/elections/{e.id}/candidacies",
            data=json.dumps(payload),
            content_type="application/json",
        )
    assert r.status_code == 201, r.content
    cid = r.json()["id"]

    r = client.get(f"/api/elections/{e.id}/candidacies")
    assert r.status_code == 200
    assert any(row["id"] == cid for row in r.json()["results"])

    r = client.patch(f"/api/candidacies/{cid}", data=json.dumps({"credentials":"BSCS, Cum Laude"}), content_type="application/json")
    assert r.status_code == 200

    r = client.delete(f"/api/candidacies/{cid}")
    assert r.status_code == 204

def test_officer_cannot_write(db):
    client = APIClient()
    e = _current_election()
    officer = _officer_user()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {_token(officer)}")
    r = client.post(f"/api/elections/{e.id}/candidacies", data=json.dumps({"candidateUserId": 999999}), content_type="application/json")
    assert r.status_code == 403
