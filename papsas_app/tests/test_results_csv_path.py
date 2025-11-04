from rest_framework.test import APIClient


def test_results_csv_canonical(officer_user, sample_election):
    c = APIClient(); c.force_authenticate(officer_user)
    r = c.get(f'/api/elections/{sample_election.id}/results/export.csv')
    assert r.status_code == 200
    assert str(r['Content-Type']).startswith('text/csv')


def test_results_csv_filename(officer_user, sample_election):
    c = APIClient(); c.force_authenticate(officer_user)
    r = c.get(f'/api/elections/{sample_election.id}/results/export.csv')
    assert r.status_code == 200
    cd = r.get('Content-Disposition', '')
    assert 'results-election-' in cd and (cd.lower().endswith('.csv"') or cd.lower().endswith('.csv'))
