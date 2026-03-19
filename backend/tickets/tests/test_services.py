import pytest

from shared.exceptions import InvalidTransitionError, NotFoundError
from tickets.models import TicketStatus
from tickets.services import add_comment, create_ticket, get_ticket, transition_ticket


@pytest.mark.django_db
class TestTicketServices:
    def test_create_ticket(self):
        ticket = create_ticket(
            subject="Cannot login",
            body="I get a 500 error when trying to login.",
            contact_email="user@example.com",
        )
        assert ticket.subject == "Cannot login"
        assert ticket.status == TicketStatus.OPEN

    def test_get_ticket_not_found(self):
        from uuid import uuid4

        with pytest.raises(NotFoundError):
            get_ticket(ticket_id=uuid4())

    def test_transition_ticket(self):
        ticket = create_ticket(
            subject="Test",
            body="Test body",
            contact_email="test@example.com",
        )
        updated = transition_ticket(ticket_id=ticket.id, new_status=TicketStatus.TRIAGED)
        assert updated.status == TicketStatus.TRIAGED

    def test_invalid_transition(self):
        ticket = create_ticket(
            subject="Test",
            body="Test body",
            contact_email="test@example.com",
        )
        with pytest.raises(InvalidTransitionError):
            transition_ticket(ticket_id=ticket.id, new_status=TicketStatus.RESOLVED)

    def test_add_comment(self):
        ticket = create_ticket(
            subject="Test",
            body="Test body",
            contact_email="test@example.com",
        )
        comment = add_comment(
            ticket_id=ticket.id,
            body="Looking into this.",
            author_name="Agent Smith",
        )
        assert comment.ticket_id == ticket.id
        assert comment.author_name == "Agent Smith"
