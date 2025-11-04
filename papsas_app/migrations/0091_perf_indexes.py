from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("papsas_app", "0090_candidacy_add_position_fk"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="vote",
            index=models.Index(fields=["election"], name="ix_vote_election"),
        ),
        migrations.AddIndex(
            model_name="voteselection",
            index=models.Index(fields=["candidate"], name="ix_vsel_candidate"),
        ),
        migrations.AddIndex(
            model_name="candidacy",
            index=models.Index(fields=["election"], name="ix_cand_election"),
        ),
        migrations.AddIndex(
            model_name="candidacy",
            index=models.Index(fields=["position"], name="ix_cand_position"),
        ),
        migrations.AddConstraint(
            model_name="candidacy",
            constraint=models.UniqueConstraint(fields=["election", "candidate", "position"], name="uq_cand_elec_user_pos"),
        ),
    ]

