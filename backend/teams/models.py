from django.conf import settings
from django.db import models

from shared.models import UUIDModel


class Team(UUIDModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class TeamMember(UUIDModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[("lead", "Lead"), ("agent", "Agent")],
        default="agent",
    )

    class Meta:
        unique_together = ("team", "user")

    def __str__(self) -> str:
        return f"{self.user} ({self.role}) in {self.team}"


class RoutingRule(UUIDModel):
    """Maps classification categories to teams."""

    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="routing_rules")

    class Meta:
        ordering = ["category", "priority"]

    def __str__(self) -> str:
        return f"{self.category}/{self.priority} -> {self.team}"


class Assignment(UUIDModel):
    """Tracks which team/agent a ticket is assigned to."""

    ticket_id = models.UUIDField(db_index=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="assignments")
    agent = models.ForeignKey(
        TeamMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Ticket {self.ticket_id} -> {self.team}"
