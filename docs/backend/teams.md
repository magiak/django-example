# Teams — Bounded Context

**Location:** `backend/teams/`

## Purpose

The teams context manages teams, team members, and routing rules. After triage produces a classification, this context decides which team gets the ticket and optionally auto-assigns an agent.

## Domain Concepts

- **Team** — a group of support agents with a specialization
- **TeamMember** — a user assigned to a team with a role (lead or agent)
- **RoutingRule** — maps classification categories/priorities to teams
- **Assignment** — links a ticket to a team (and optionally a specific agent)

## Models

### Team

```python
class Team(UUIDModel):
    name: CharField(100, unique=True)
    description: TextField(blank=True)
```

### TeamMember

```python
class TeamMember(UUIDModel):
    team: ForeignKey(Team)
    user: ForeignKey(User)  # Django auth user
    role: CharField  # "lead" or "agent"
    # unique_together: (team, user)
```

### RoutingRule

```python
class RoutingRule(UUIDModel):
    category: CharField(100)     # matches Classification.category
    priority: CharField(20)      # optional — blank means "match all priorities"
    team: ForeignKey(Team)
```

### Assignment

```python
class Assignment(UUIDModel):
    ticket_id: UUIDField          # loose coupling — not a FK to Ticket
    team: ForeignKey(Team)
    agent: ForeignKey(TeamMember)  # nullable — auto-assignment is optional
```

Note: `Assignment.ticket_id` is a plain UUID field, not a foreign key. This keeps the teams context loosely coupled from the tickets context.

## Services (`services.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `list_teams` | `() -> list[Team]` | Returns all teams |
| `route_ticket` | `(ticket_id, category, priority) -> Assignment \| None` | Matches routing rules and creates/updates assignment |
| `get_assignment` | `(ticket_id) -> Assignment \| None` | Returns current assignment for a ticket |

### Routing Logic

`route_ticket()` uses a two-step matching strategy:

1. **Exact match** — find a rule matching both `category` AND `priority`
2. **Fallback** — find a rule matching `category` with blank priority (catch-all)
3. **No match** — returns `None` (ticket remains unassigned)

Assignments use `update_or_create` — re-routing a ticket replaces the previous assignment.

## Tasks (`tasks.py`)

### `route_ticket_task`

```python
@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60000)
def route_ticket_task(ticket_id: str, category: str, priority: str) -> None:
```

- Called after classification completes
- Receives classification results as primitive args
- Logs success or warns if no matching rule found

## API Endpoints

| Method | Path | Response | Status Codes |
|--------|------|----------|-------------|
| `GET` | `/api/teams/` | `list[TeamOut]` | 200 |
| `GET` | `/api/teams/assignments/{ticket_id}` | `AssignmentOut` | 200, 404 |

## Data Flow

```
Classification Saved
    → teams.tasks.route_ticket_task(ticket_id, category, priority)  [Dramatiq]
    → teams.services.route_ticket(ticket_id, category, priority)
    → Match RoutingRule by category + priority
    → Create/update Assignment
    → Ticket is now assigned to a team
```
