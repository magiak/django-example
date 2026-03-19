import pytest
from django.test import Client

from .factories import TicketFactory


@pytest.mark.django_db
class TestTicketAPI:
    def setup_method(self):
        self.client = Client()

    def test_create_ticket(self):
        response = self.client.post(
            "/api/tickets/",
            data={
                "subject": "Help needed",
                "body": "I cannot access my account.",
                "contact_email": "user@example.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["subject"] == "Help needed"
        assert data["status"] == "open"

    def test_list_tickets(self):
        TicketFactory.create_batch(3)
        response = self.client.get("/api/tickets/")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_get_ticket(self):
        ticket = TicketFactory(subject="Specific ticket")
        response = self.client.get(f"/api/tickets/{ticket.id}")
        assert response.status_code == 200
        assert response.json()["subject"] == "Specific ticket"

    def test_get_ticket_not_found(self):
        import uuid

        response = self.client.get(f"/api/tickets/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_update_status(self):
        ticket = TicketFactory()
        response = self.client.patch(
            f"/api/tickets/{ticket.id}/status",
            data={"status": "triaged"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "triaged"

    def test_add_comment(self):
        ticket = TicketFactory()
        response = self.client.post(
            f"/api/tickets/{ticket.id}/comments",
            data={"body": "Working on it.", "author_name": "Agent"},
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["body"] == "Working on it."
