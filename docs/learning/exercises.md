# Hands-On Exercises

Practice what you learned. Each exercise targets specific skills.

---

## Exercise 1: Add a Field

**Skills:** Models, schemas, migrations

Add a `source` field to Ticket that tracks where the ticket came from (e.g., "email", "web", "api").

### Steps

1. **Model** — Add the field in `tickets/models.py`:
   ```python
   class TicketSource(models.TextChoices):
       EMAIL = "email", "Email"
       WEB = "web", "Web"
       API = "api", "API"

   class Ticket(UUIDModel):
       # ... existing fields ...
       source = models.CharField(
           max_length=20,
           choices=TicketSource.choices,
           default=TicketSource.WEB,
       )
   ```

2. **Schemas** — Add to `TicketIn` and `TicketOut` in `tickets/schemas.py`:
   ```python
   class TicketIn(Schema):
       source: str = "web"    # default value
   ```

3. **Migrate** — Generate and apply:
   ```bash
   make makemigrations
   make migrate
   ```

4. **Verify** — Check the API docs at `/api/docs` — the field should appear.

---

## Exercise 2: Add a New Endpoint

**Skills:** Services, API, tests

Add `DELETE /api/tickets/{ticket_id}` that deletes a ticket.

### Steps

1. **Service** — Add in `tickets/services.py`:
   ```python
   def delete_ticket(*, ticket_id: UUID) -> None:
       deleted, _ = Ticket.objects.filter(id=ticket_id).delete()
       if deleted == 0:
           raise NotFoundError("Ticket", str(ticket_id))
   ```

2. **API** — Add in `tickets/api.py`:
   ```python
   @router.delete("/{ticket_id}", response={204: None, 404: dict})
   def delete_ticket(request, ticket_id: UUID):
       try:
           services.delete_ticket(ticket_id=ticket_id)
           return 204, None
       except NotFoundError as e:
           return 404, {"detail": e.message}
   ```

3. **Test** — Add in `tickets/tests/test_api.py`:
   ```python
   def test_delete_ticket(self):
       ticket = TicketFactory()
       response = self.client.delete(f"/api/tickets/{ticket.id}")
       assert response.status_code == 204

   def test_delete_ticket_not_found(self):
       import uuid
       response = self.client.delete(f"/api/tickets/{uuid.uuid4()}")
       assert response.status_code == 404
   ```

4. **Run tests** — `make test`

---

## Exercise 3: Add a New Bounded Context

**Skills:** Full DDD app from scratch

Create a `notifications` app that tracks email notifications for tickets.

### Steps

1. **Create the directory structure:**
   ```bash
   mkdir -p backend/notifications/{tests,migrations}
   touch backend/notifications/__init__.py
   touch backend/notifications/apps.py
   touch backend/notifications/models.py
   touch backend/notifications/services.py
   touch backend/notifications/api.py
   touch backend/notifications/schemas.py
   touch backend/notifications/tasks.py
   touch backend/notifications/{tests,migrations}/__init__.py
   ```

2. **Create the app config** — `notifications/apps.py`

3. **Define the model** — `Notification` with fields: `ticket_id`, `recipient_email`, `subject`, `sent_at` (nullable), `status` (pending/sent/failed)

4. **Register** in `INSTALLED_APPS` in `config/settings/base.py`

5. **Add router** in `config/urls.py`

6. **Create services, schemas, API** following the same patterns as tickets

7. **Run** `make makemigrations` and `make migrate`

---

## Exercise 4: Wire the Async Pipeline

**Skills:** Dramatiq tasks, cross-context communication

Connect the full pipeline: creating a ticket triggers classification.

### Steps

1. **In `tickets/services.py`** — Uncomment the task call:
   ```python
   def create_ticket(*, subject, body, contact_email):
       ticket = Ticket.objects.create(...)
       # Uncomment this line:
       from triage.tasks import classify_ticket_task
       classify_ticket_task.send(str(ticket.id))
       return ticket
   ```

2. **Start the worker:**
   ```bash
   make up    # ensures worker container is running
   ```

3. **Create a ticket via API:**
   ```bash
   curl -X POST http://localhost:8000/api/tickets/ \
     -H "Content-Type: application/json" \
     -d '{"subject": "Test async", "body": "Testing the pipeline", "contact_email": "test@example.com"}'
   ```

4. **Check the classification was created:**
   ```bash
   curl http://localhost:8000/api/triage/{ticket_id}/classification
   ```

5. **Check worker logs:**
   ```bash
   docker compose logs worker
   ```

---

**Back to:** [Learning Path Overview →](../learning-path.md)
