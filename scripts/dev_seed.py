# scripts/dev_seed.py
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from papsas_app.models import (
    MembershipTypes, UserMembership, Election, Candidacy
)

User = get_user_model()

def set_if_exists(obj, **kwargs):
    """Set attributes only if the model has those fields."""
    for k, v in kwargs.items():
        if hasattr(obj, k):
            setattr(obj, k, v)

@transaction.atomic
def run():
    # 0) normal (non-admin) user
    user, _ = User.objects.get_or_create(
        email="normal@example.com",
        defaults={"username": "normal_user", "is_staff": False, "is_superuser": False},
    )
    if not user.has_usable_password():
        user.set_password("P@ssw0rd!")
        user.save()

    # 1) membership type and link
    mt, _ = MembershipTypes.objects.get_or_create(name="Student")
    UserMembership.objects.get_or_create(user=user, membership_type=mt)

    # 2) election (active now)
    now = timezone.now()
    elec_defaults = {}
    # handle common field names
    set_if_exists(elec_defaults, start_date=now, end_date=now + timezone.timedelta(days=7))
    set_if_exists(elec_defaults, start_at=now, end_at=now + timezone.timedelta(days=7))
    elec, _ = Election.objects.get_or_create(
        **({"title": "Dev Election"} if hasattr(Election, "_meta") else {}),
        defaults=elec_defaults or {"id": 1},  # fallback if title not present
    )
    # ensure dates are set (if model uses different names)
    set_if_exists(elec, start_date=now, end_date=now + timezone.timedelta(days=7))
    set_if_exists(elec, start_at=now, end_at=now + timezone.timedelta(days=7))
    if hasattr(elec, "is_active") and getattr(elec, "is_active") is not True:
        elec.is_active = True
    elec.save()

    # 3) candidates for that election (covering common field names)
    def add_candidate(name):
        cand_defaults = {}
        # possible field names
        set_if_exists(cand_defaults, candidate_name=name, name=name, full_name=name)
        c, created = Candidacy.objects.get_or_create(
            **({"election": elec} if "election" in [f.name for f in Candidacy._meta.get_fields()] else {}),
            defaults=cand_defaults or {},
        )
        # ensure foreign key set
        if hasattr(c, "election") and c.election_id is None:
            c.election = elec
        if hasattr(c, "candidate_name") and not c.candidate_name:
            c.candidate_name = name
        if hasattr(c, "name") and not getattr(c, "name", None):
            c.name = name
        c.save()
        return c

    add_candidate("Alice A.")
    add_candidate("Bob B.")

    print("Seed OK: user=normal@example.com / P@ssw0rd!, election + 2 candidates")

if __name__ == "__main__":
    run()
