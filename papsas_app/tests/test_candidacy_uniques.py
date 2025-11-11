# papsas_app/tests/test_candidacy_uniques.py
from django.test import TestCase
from django.db import connection
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from papsas_app.models import Election
from papsas_app.models_position import Position
from papsas_app.models import Candidacy  # adjust import path if Candidacy is in a different module

def _is_postgres() -> bool:
    return connection.vendor == "postgresql"

class CandidacyPartialUniquesPostgresTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="cand_tester", email="cand@test.local")
        # electionStatus is non-nullable in the current model; set it explicitly.
        cls.elec = Election.objects.create(title="Test Elec", numWinners=1, electionStatus=True)
        cls.pos1 = Position.objects.create(election=cls.elec, title="Director", winners=1)
        cls.pos2 = Position.objects.create(election=cls.elec, title="President", winners=1)

    def test_skip_if_not_postgres(self):
        # Make it explicit in output why the rest might be skipped
        self.assertIn(connection.vendor, ("postgresql", "sqlite", "mysql", "oracle"))

    def test_positionless_duplicate_rejected_on_postgres(self):
        if not _is_postgres():
            self.skipTest("Partial unique index only enforced on PostgreSQL.")
        # First at-large candidacy (position=None)
        Candidacy.objects.create(election=self.elec, position=None, candidate=self.user)
        # Second identical row should violate ux_cand_elec_nullpos
        with self.assertRaises(IntegrityError):
            Candidacy.objects.create(election=self.elec, position=None, candidate=self.user)

    def test_same_position_duplicate_rejected_on_postgres(self):
        if not _is_postgres():
            self.skipTest("Partial unique index only enforced on PostgreSQL.")
        Candidacy.objects.create(election=self.elec, position=self.pos1, candidate=self.user)
        with self.assertRaises(IntegrityError):
            Candidacy.objects.create(election=self.elec, position=self.pos1, candidate=self.user)

    def test_different_positions_allowed(self):
        # This should be allowed even on Postgres: uniqueness is (election, position, candidate)
        Candidacy.objects.create(election=self.elec, position=self.pos1, candidate=self.user)
        Candidacy.objects.create(election=self.elec, position=self.pos2, candidate=self.user)  # no IntegrityError
