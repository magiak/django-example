import pytest

from shared.exceptions import InvalidTransitionError
from tickets.models import TicketStatus

from .factories import TicketFactory


@pytest.mark.django_db
class TestTicketModel:
    def test_create_ticket(self):
        ticket = TicketFactory()
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority is None
        assert ticket.version == 1

    def test_valid_transition(self):
        ticket = TicketFactory()
        ticket.transition_to(TicketStatus.TRIAGED)
        assert ticket.status == TicketStatus.TRIAGED
        assert ticket.version == 2

    def test_invalid_transition_raises(self):
        ticket = TicketFactory()
        with pytest.raises(InvalidTransitionError):
            ticket.transition_to(TicketStatus.RESOLVED)

    def test_full_lifecycle(self):
        ticket = TicketFactory()
        ticket.transition_to(TicketStatus.TRIAGED)
        ticket.transition_to(TicketStatus.IN_PROGRESS)
        ticket.transition_to(TicketStatus.RESOLVED)
        ticket.transition_to(TicketStatus.CLOSED)
        assert ticket.status == TicketStatus.CLOSED
        assert ticket.version == 5
