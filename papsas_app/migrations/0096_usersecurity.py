from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_user_security(apps, schema_editor):
    User = apps.get_model("papsas_app", "User")
    UserSecurity = apps.get_model("papsas_app", "UserSecurity")
    for user in User.objects.all():
        UserSecurity.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ("papsas_app", "0095_candidacy_constraints"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserSecurity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email_verified_at", models.DateTimeField(blank=True, null=True)),
                ("otp_hash", models.CharField(blank=True, max_length=128)),
                ("otp_expires_at", models.DateTimeField(blank=True, null=True)),
                ("otp_attempts", models.PositiveSmallIntegerField(default=0)),
                ("otp_locked_until", models.DateTimeField(blank=True, null=True)),
                ("otp_last_sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="security",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.RunPython(create_user_security, reverse_code=migrations.RunPython.noop),
    ]
