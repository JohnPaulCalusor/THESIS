from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Ensure smokebot test user exists"

    def handle(self, *args, **kwargs):
        U = get_user_model()
        u, created = U.objects.get_or_create(
            username="smokebot@example.com",
            defaults={"email": "smokebot@example.com", "is_active": True},
        )
        u.set_password("ChangeMe123!")
        u.is_active = True
        u.save()
        self.stdout.write(self.style.SUCCESS(
            f"smokebot: {'created' if created else 'updated'}"
        ))
