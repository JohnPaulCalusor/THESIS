from django.db import models
from .models import Election


class Position(models.Model):
    election = models.ForeignKey(Election, related_name="positions", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    sort = models.PositiveIntegerField(default=0)
    winners = models.IntegerField(
        null=True,
        blank=True,
        help_text="Max winners for this position; null means use election-level rule.",
    )

    @property
    def effective_winners(self) -> int:
        """Return the effective winner count, defaulting to at least one choice."""
        return self.winners or 1

    class Meta:
        unique_together = ("election", "title")
        ordering = ("sort", "id")

    def __str__(self):
        return f"{self.title} (E{self.election_id})"
