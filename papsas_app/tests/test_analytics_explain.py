from rest_framework.test import APIClient


def test_analytics_officer_ok(officer_user, sample_election):
    c = APIClient(); c.force_authenticate(officer_user)
    r = c.get(f'/api/elections/{sample_election.id}/analytics')
    assert r.status_code == 200
    j = r.json()
    assert 'positions' in j and 'meta' in j and 'totalVotes' in j['meta']


def test_explain_officer_ok(officer_user, sample_election):
    c = APIClient(); c.force_authenticate(officer_user)
    r = c.post(f'/api/elections/{sample_election.id}/explain', {}, format='json')
    assert r.status_code == 200
    j = r.json()
    assert 'short' in j and 'long' in j


def test_analytics_member_forbidden(member_user, sample_election):
    c = APIClient(); c.force_authenticate(member_user)
    assert c.get(f'/api/elections/{sample_election.id}/analytics').status_code == 403

