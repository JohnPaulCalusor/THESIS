from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Normalize role flags: admins -> is_staff True; officers (non-admin) -> is_staff False."

    def handle(self, *args, **opts):
        U = get_user_model()
        admin_grp, _ = Group.objects.get_or_create(name="admin")
        officer_grp, _ = Group.objects.get_or_create(name="officer")

        # Admins: ensure is_staff=True
        admins = U.objects.filter(groups=admin_grp)
        n_admins = admins.exclude(is_staff=True).update(is_staff=True)

        # Officers (who are not also admins): ensure is_staff=False
        officers = U.objects.filter(groups=officer_grp).exclude(groups=admin_grp)
        n_off = officers.filter(is_staff=True).update(is_staff=False)

        self.stdout.write(self.style.SUCCESS(f"Updated {n_admins} admins, {n_off} officers"))
