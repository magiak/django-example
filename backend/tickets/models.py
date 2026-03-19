from django.db import models

from shared.exceptions import InvalidTransitionError
from shared.models import UUIDModel


class TicketStatus(models.TextChoices):
    OPEN = "open", "Open"
    TRIAGED = "triaged", "Triaged"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"


class TicketPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    CRITICAL = "critical", "Critical"


# Valid state transitions — like a state machine
VALID_TRANSITIONS: dict[str, list[str]] = {
    TicketStatus.OPEN: [TicketStatus.TRIAGED, TicketStatus.CLOSED],
    TicketStatus.TRIAGED: [TicketStatus.IN_PROGRESS, TicketStatus.CLOSED],
    TicketStatus.IN_PROGRESS: [TicketStatus.RESOLVED, TicketStatus.TRIAGED],
    TicketStatus.RESOLVED: [TicketStatus.CLOSED, TicketStatus.IN_PROGRESS],
    TicketStatus.CLOSED: [TicketStatus.OPEN],  # reopen
}


class Ticket(UUIDModel):
    subject = models.CharField(max_length=200)
    body = models.TextField()
    contact_email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=TicketStatus.choices,
        default=TicketStatus.OPEN,
        db_index=True,
    )
    priority = models.CharField(
        max_length=20,
        choices=TicketPriority.choices,
        null=True,
        blank=True,
    )
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.status}] {self.subject}"

    def transition_to(self, new_status: str) -> None:
        """Enforce valid status transitions."""
        allowed = VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise InvalidTransitionError("Ticket", self.status, new_status)
        self.status = new_status
        self.version += 1


class Comment(UUIDModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    author_name = models.CharField(max_length=100)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author_name} on {self.ticket_id}"
