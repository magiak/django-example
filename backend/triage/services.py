from uuid import UUID

from shared.exceptions import NotFoundError
from tickets.models import Ticket

from .models import Classification


def get_classification(*, ticket_id: UUID) -> Classification:
    """Get the classification for a ticket."""
    try:
        return Classification.objects.get(ticket_id=ticket_id)
    except Classification.DoesNotExist:
        raise NotFoundError("Classification", str(ticket_id))


def classify_ticket(*, ticket_id: UUID) -> Classification:
    """Classify a ticket using LLM. Idempotent — skips if already classified for current version."""
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        raise NotFoundError("Ticket", str(ticket_id))

    # Idempotency: skip if already classified for this version
    existing = Classification.objects.filter(ticket=ticket, ticket_version=ticket.version).first()
    if existing:
        return existing

    # TODO: Replace with real LLM call in Session 2
    result = {
        "category": "general_inquiry",
        "priority_suggestion": "medium",
        "sentiment": "neutral",
        "confidence": 0.85,
        "model_used": "mock",
    }

    classification = Classification.objects.create(
        ticket=ticket,
        ticket_version=ticket.version,
        **result,
    )
    return classification
