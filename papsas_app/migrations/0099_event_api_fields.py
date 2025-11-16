from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


def _populate_event_slugs(apps, schema_editor):
    Event = apps.get_model("papsas_app", "Event")
    for event in Event.objects.filter(slug__isnull=True):
        base = slugify(event.eventName or "event")
        if not base:
            base = "event"
        candidate = base
        counter = 1
        while Event.objects.exclude(pk=event.pk).filter(slug=candidate).exists():
            counter += 1
            candidate = f"{base}-{counter}"
        event.slug = candidate
        event.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("papsas_app", "0098_votechoice"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="cover_image",
            field=models.ImageField(blank=True, null=True, upload_to="events/"),
        ),
        migrations.AddField(
            model_name="event",
            name="slug",
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="event",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="events_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(_populate_event_slugs, migrations.RunPython.noop),
    ]
