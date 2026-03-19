# API Endpoints

Base URL: `http://localhost:8000/api`

Interactive docs (Swagger UI): [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

## Tickets

### Create Ticket

```
POST /api/tickets/
```

**Request:**
```json
{
  "subject": "Cannot login to dashboard",
  "body": "I get a 500 error when clicking the login button.",
  "contact_email": "user@example.com"
}
```

**Response (201):**
```json
{
  "id": "a1b2c3d4-...",
  "subject": "Cannot login to dashboard",
  "status": "open",
  "priority": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

```bash
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Content-Type: application/json" \
  -d '{"subject": "Cannot login", "body": "500 error on login", "contact_email": "user@example.com"}'
```

---

### List Tickets

```
GET /api/tickets/
```

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter by status (open, triaged, in_progress, resolved, closed) |
| `priority` | string | Filter by priority (low, medium, high, critical) |

**Response (200):** Array of `TicketOut`

```bash
# All tickets
curl http://localhost:8000/api/tickets/

# Filter by status
curl http://localhost:8000/api/tickets/?status=open

# Filter by priority
curl http://localhost:8000/api/tickets/?priority=high
```

---

### Get Ticket Detail

```
GET /api/tickets/{ticket_id}
```

**Response (200):**
```json
{
  "id": "a1b2c3d4-...",
  "subject": "Cannot login to dashboard",
  "body": "I get a 500 error when clicking the login button.",
  "contact_email": "user@example.com",
  "status": "open",
  "priority": null,
  "version": 1,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "comments": []
}
```

**Response (404):**
```json
{"detail": "Ticket with id 'xxx' not found"}
```

```bash
curl http://localhost:8000/api/tickets/a1b2c3d4-...
```

---

### Update Ticket Status

```
PATCH /api/tickets/{ticket_id}/status
```

**Request:**
```json
{"status": "triaged"}
```

**Response (200):** Updated `TicketOut`

**Response (400):** Invalid transition
```json
{"detail": "Cannot transition Ticket from 'open' to 'resolved'"}
```

**Response (404):** Ticket not found

```bash
curl -X PATCH http://localhost:8000/api/tickets/a1b2c3d4-.../status \
  -H "Content-Type: application/json" \
  -d '{"status": "triaged"}'
```

---

### Add Comment

```
POST /api/tickets/{ticket_id}/comments
```

**Request:**
```json
{
  "body": "Looking into this issue now.",
  "author_name": "Support Agent"
}
```

**Response (201):**
```json
{
  "id": "e5f6g7h8-...",
  "body": "Looking into this issue now.",
  "author_name": "Support Agent",
  "created_at": "2025-01-15T11:00:00Z"
}
```

```bash
curl -X POST http://localhost:8000/api/tickets/a1b2c3d4-.../comments \
  -H "Content-Type: application/json" \
  -d '{"body": "Looking into this.", "author_name": "Agent Smith"}'
```

---

## Triage

### Get Classification

```
GET /api/triage/{ticket_id}/classification
```

**Response (200):**
```json
{
  "id": "b2c3d4e5-...",
  "ticket_id": "a1b2c3d4-...",
  "category": "authentication",
  "priority_suggestion": "high",
  "sentiment": "frustrated",
  "confidence": 0.92,
  "model_used": "gpt-4",
  "created_at": "2025-01-15T10:30:05Z"
}
```

**Response (404):** No classification exists yet

```bash
curl http://localhost:8000/api/triage/a1b2c3d4-.../classification
```

---

## Teams

### List Teams

```
GET /api/teams/
```

**Response (200):**
```json
[
  {
    "id": "c3d4e5f6-...",
    "name": "Authentication Team",
    "description": "Handles login, SSO, and access control issues",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

```bash
curl http://localhost:8000/api/teams/
```

---

### Get Ticket Assignment

```
GET /api/teams/assignments/{ticket_id}
```

**Response (200):**
```json
{
  "id": "d4e5f6g7-...",
  "ticket_id": "a1b2c3d4-...",
  "team": {
    "id": "c3d4e5f6-...",
    "name": "Authentication Team",
    "description": "...",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "created_at": "2025-01-15T10:30:10Z"
}
```

**Response (404):** No assignment found

```bash
curl http://localhost:8000/api/teams/assignments/a1b2c3d4-...
```

---

## Response Schemas Summary

| Schema | Fields |
|--------|--------|
| `TicketOut` | id, subject, status, priority, created_at, updated_at |
| `TicketDetailOut` | id, subject, body, contact_email, status, priority, version, created_at, updated_at, comments |
| `CommentOut` | id, body, author_name, created_at |
| `ClassificationOut` | id, ticket_id, category, priority_suggestion, sentiment, confidence, model_used, created_at |
| `TeamOut` | id, name, description, created_at |
| `AssignmentOut` | id, ticket_id, team (nested TeamOut), created_at |
