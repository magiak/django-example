from django.db import models

from shared.models import UUIDModel
from tickets.models import Ticket


class Classification(UUIDModel):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="classification")
    category = models.CharField(max_length=100)
    priority_suggestion = models.CharField(max_length=20)
    sentiment = models.CharField(max_length=20)
    confidence = models.FloatField()
    model_used = models.CharField(max_length=100)
    ticket_version = models.PositiveIntegerField(
        help_text="Ticket version at time of classification, for idempotency."
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Classification for {self.ticket_id}: {self.category} ({self.confidence:.0%})"
