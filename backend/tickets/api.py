from uuid import UUID

from ninja import Router

from shared.exceptions import DomainError, NotFoundError

from . import services
from .schemas import (
    CommentIn,
    CommentOut,
    TicketDetailOut,
    TicketIn,
    TicketOut,
    TicketStatusIn,
)

router = Router(tags=["Tickets"])


@router.post("/", response={201: TicketOut})
def create_ticket(request, payload: TicketIn):
    ticket = services.create_ticket(
        subject=payload.subject,
        body=payload.body,
        contact_email=payload.contact_email,
    )
    return 201, ticket


@router.get("/", response=list[TicketOut])
def list_tickets(request, status: str | None = None, priority: str | None = None):
    return services.list_tickets(status=status, priority=priority)


@router.get("/{ticket_id}", response={200: TicketDetailOut, 404: dict})
def get_ticket(request, ticket_id: UUID):
    try:
        return services.get_ticket(ticket_id=ticket_id)
    except NotFoundError as e:
        return 404, {"detail": e.message}


@router.patch("/{ticket_id}/status", response={200: TicketOut, 400: dict, 404: dict})
def update_ticket_status(request, ticket_id: UUID, payload: TicketStatusIn):
    try:
        ticket = services.transition_ticket(ticket_id=ticket_id, new_status=payload.status)
        return ticket
    except NotFoundError as e:
        return 404, {"detail": e.message}
    except DomainError as e:
        return 400, {"detail": e.message}


@router.post("/{ticket_id}/comments", response={201: CommentOut, 404: dict})
def add_comment(request, ticket_id: UUID, payload: CommentIn):
    try:
        comment = services.add_comment(
            ticket_id=ticket_id,
            body=payload.body,
            author_name=payload.author_name,
        )
        return 201, comment
    except NotFoundError as e:
        return 404, {"detail": e.message}
