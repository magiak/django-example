from uuid import UUID

from django.db import transaction

from shared.exceptions import NotFoundError

from .models import Comment, Ticket


def create_ticket(*, subject: str, body: str, contact_email: str) -> Ticket:
    """Create a new support ticket and trigger async triage."""
    ticket = Ticket.objects.create(
        subject=subject,
        body=body,
        contact_email=contact_email,
    )
    # Trigger async classification via Dramatiq
    from triage.tasks import classify_ticket_task
    classify_ticket_task.send(str(ticket.id))
    return ticket


def get_ticket(*, ticket_id: UUID) -> Ticket:
    """Retrieve a ticket by ID or raise NotFoundError."""
    try:
        return Ticket.objects.prefetch_related("comments").get(id=ticket_id)
    except Ticket.DoesNotExist:
        raise NotFoundError("Ticket", str(ticket_id))


def list_tickets(*, status: str | None = None, priority: str | None = None) -> list[Ticket]:
    """List tickets with optional filters."""
    qs = Ticket.objects.all()
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    return list(qs)


@transaction.atomic
def transition_ticket(*, ticket_id: UUID, new_status: str) -> Ticket:
    """Transition ticket status with optimistic concurrency."""
    ticket = Ticket.objects.select_for_update().get(id=ticket_id)
    ticket.transition_to(new_status)
    ticket.save()
    return ticket


def add_comment(*, ticket_id: UUID, body: str, author_name: str) -> Comment:
    """Add a comment to a ticket."""
    if not Ticket.objects.filter(id=ticket_id).exists():
        raise NotFoundError("Ticket", str(ticket_id))
    return Comment.objects.create(
        ticket_id=ticket_id,
        body=body,
        author_name=author_name,
    )
