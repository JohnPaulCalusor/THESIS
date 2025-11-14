from django.db import migrations, models


def backfill_vote_choices(apps, schema_editor):
    Vote = apps.get_model("papsas_app", "Vote")
    VoteChoice = apps.get_model("papsas_app", "VoteChoice")
    Candidacy = apps.get_model("papsas_app", "Candidacy")
    db_alias = schema_editor.connection.alias

    through = Vote.candidateID.through
    for vote in Vote.objects.using(db_alias).all().iterator():
        links = (
            through.objects.using(db_alias)
            .filter(vote_id=vote.id)
            .values_list("candidacy_id", flat=True)
        )
        seen = set()
        create = []
        for candidacy_id in links:
            if candidacy_id in seen:
                continue
            seen.add(candidacy_id)
            candidacy = (
                Candidacy.objects.using(db_alias)
                .filter(id=candidacy_id)
                .select_related("position")
                .first()
            )
            if not candidacy or candidacy.position_id is None:
                continue
            create.append(
                VoteChoice(
                    vote_id=vote.id,
                    candidacy_id=candidacy.id,
                    position_id=candidacy.position_id,
                )
            )
        if create:
            VoteChoice.objects.using(db_alias).bulk_create(create, ignore_conflicts=True)


class Migration(migrations.Migration):

    dependencies = [
        ("papsas_app", "0097_alter_usersecurity_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="VoteChoice",
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
                    "vote",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="choices",
                        to="papsas_app.Vote",
                    ),
                ),
                (
                    "candidacy",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        related_name="vote_choices",
                        to="papsas_app.Candidacy",
                    ),
                ),
                (
                    "position",
                    models.ForeignKey(
                        on_delete=models.PROTECT,
                        related_name="vote_choices",
                        to="papsas_app.Position",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="votechoice",
            constraint=models.UniqueConstraint(
                fields=["vote", "candidacy"], name="uq_choice_vote_candidacy"
            ),
        ),
        migrations.RunPython(backfill_vote_choices, reverse_code=migrations.RunPython.noop),
    ]
