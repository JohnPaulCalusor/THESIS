from django.contrib.postgres.indexes import GinIndex
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("analytics", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="auditevent",
            index=GinIndex(fields=["meta"], name="analytics_a_meta_gin_idx"),
        ),
    ]
