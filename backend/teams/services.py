from uuid import UUID

from .models import Assignment, RoutingRule, Team


def list_teams() -> list[Team]:
    return list(Team.objects.all())


def route_ticket(*, ticket_id: UUID, category: str, priority: str) -> Assignment | None:
    """Route a ticket to a team based on classification results."""
    # Try exact match (category + priority)
    rule = RoutingRule.objects.filter(category=category, priority=priority).first()

    # Fallback to category-only match
    if not rule:
        rule = RoutingRule.objects.filter(category=category, priority="").first()

    if not rule:
        return None

    assignment, _created = Assignment.objects.update_or_create(
        ticket_id=ticket_id,
        defaults={"team": rule.team},
    )
    return assignment


def get_assignment(*, ticket_id: UUID) -> Assignment | None:
    return Assignment.objects.select_related("team").filter(ticket_id=ticket_id).first()
