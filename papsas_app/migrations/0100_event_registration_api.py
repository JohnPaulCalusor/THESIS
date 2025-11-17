from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("papsas_app", "0099_event_api_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventSignup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="signup_records",
                        to="papsas_app.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="event_signups",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="eventsignup",
            constraint=models.UniqueConstraint(
                fields=["event", "user"], name="unique_event_signup"
            ),
        ),
    ]
