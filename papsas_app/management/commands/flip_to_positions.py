import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count

from papsas_app.models import Election, Candidacy
from papsas_app.models_position import Position


class Command(BaseCommand):
    help = "Convert an election to position-based winners with optional snapshotting."

    def add_arguments(self, parser):
        parser.add_argument("--election-id", type=int, required=True)
        parser.add_argument("--winners-default", type=int, default=1)
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--snapshot-out", type=str)
        parser.add_argument("--snapshot-in", type=str)

    def handle(self, *args, **options):
        election_id = options["election_id"]
        winners_default = options["winners_default"]
        apply_changes = options["apply"]
        snapshot_out = options.get("snapshot_out")
        snapshot_in = options.get("snapshot_in")

        if snapshot_in and not apply_changes:
            raise CommandError("--snapshot-in requires --apply.")

        try:
            election = Election.objects.get(id=election_id)
        except Election.DoesNotExist:
            raise CommandError(f"Election {election_id} not found.")

        positions = list(Position.objects.filter(election=election).order_by("id"))
        candidacy_counts = {
            row["position_id"]: row["count"]
            for row in (
                Candidacy.objects.filter(election=election)
                .values("position_id")
                .annotate(count=Count("id"))
            )
        }

        before_state = {
            "election": {"id": election.id, "numWinners": election.numWinners},
            "positions": [{"id": pos.id, "winners": pos.winners} for pos in positions],
        }

        warnings = []
        planned_positions = []
        for pos in positions:
            count = candidacy_counts.get(pos.id, 0)
            if (pos.winners or 0) > 0 and count == 0:
                warnings.append(
                    f"Position {pos.id} ({pos.title}) has winners={pos.winners} but 0 candidacies."
                )
            if not pos.winners:
                planned_positions.append(pos)

        self.stdout.write(self.style.NOTICE("Plan"))
        self.stdout.write(
            f"  Election {election.id}: numWinners -> None (position-based mode)"
        )
        for pos in planned_positions:
            self.stdout.write(
                f"  Position {pos.id}: winners {pos.winners} -> {winners_default}"
            )
        for msg in warnings:
            self.stdout.write(self.style.WARNING(msg))

        if snapshot_out:
            Path(snapshot_out).write_text(json.dumps(before_state, indent=2))
            self.stdout.write(f"Snapshot written to {snapshot_out}")

        if not apply_changes:
            self.stdout.write(self.style.SUCCESS("Dry run complete; no changes applied."))
            return

        snapshot_values = None
        if snapshot_in:
            data = json.loads(Path(snapshot_in).read_text())
            if data["election"]["id"] != election.id:
                raise CommandError("Snapshot election ID does not match.")
            snapshot_values = data

        with transaction.atomic():
            changed_positions = []
            if snapshot_values:
                election.numWinners = snapshot_values["election"]["numWinners"]
                for pos in positions:
                    target = next(
                        (item["winners"] for item in snapshot_values["positions"] if item["id"] == pos.id),
                        pos.winners,
                    )
                    if pos.winners != target:
                        pos.winners = target
                        changed_positions.append(pos)
            else:
                election.numWinners = None
                for pos in planned_positions:
                    pos.winners = winners_default
                    changed_positions.append(pos)

            election.save()
            for pos in changed_positions:
                pos.save()

            try:
                from django.core.cache import cache

                cache.clear()
            except Exception:
                pass

        after_state = {
            "election": {"id": election.id, "numWinners": election.numWinners},
            "positions": [{"id": pos.id, "winners": pos.winners} for pos in positions],
        }
        self.stdout.write(self.style.SUCCESS("Applied changes."))
        self.stdout.write(json.dumps({"before": before_state, "after": after_state}, indent=2))
