from rest_framework.test import APIClient


def test_explain_has_short_long_and_legacy_text(officer_user, sample_election):
    c = APIClient(); c.force_authenticate(officer_user)
    r = c.post(f'/api/elections/{sample_election.id}/explain', {}, format='json')
    assert r.status_code == 200
    j = r.json()
    assert 'short' in j and 'long' in j and 'text' in j
    assert isinstance(j['short'], str) and isinstance(j['long'], str) and isinstance(j['text'], str)
    assert j['text'] == j['short']

