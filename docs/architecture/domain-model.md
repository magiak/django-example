# Domain Model

## Entity Relationships

```
┌─────────────────┐         ┌──────────────────┐
│     Ticket      │ 1────1  │  Classification   │
│                 │         │  (triage context)  │
│  subject        │         │  category          │
│  body           │         │  priority_suggest.  │
│  contact_email  │         │  sentiment         │
│  status         │         │  confidence        │
│  priority       │         │  model_used        │
│  version        │         │  ticket_version    │
└──────┬──────────┘         └──────────────────┘
       │ 1
       │
       │ *
┌──────▼──────────┐         ┌──────────────────┐
│    Comment       │         │   Assignment      │
│                 │         │  (teams context)   │
│  body           │         │  ticket_id (UUID)  │──────┐
│  author_name    │         │  team (FK)         │      │
└─────────────────┘         │  agent (FK, null)  │      │
                            └──────────────────┘      │
                                                       │
┌─────────────────┐         ┌──────────────────┐      │
│      Team       │ 1────*  │   TeamMember      │      │
│                 │         │                   │      │
│  name           │         │  user (FK)        │      │
│  description    │         │  role             │      │
└──────┬──────────┘         └──────────────────┘      │
       │ 1                                            │
       │                                              │
       │ *                                            │
┌──────▼──────────┐                                   │
│  RoutingRule    │                                   │
│                 │    (Assignment.ticket_id          │
│  category       │     references Ticket.id          │
│  priority       │     but is stored as UUID,       │
│  team (FK)      │     not as a foreign key)        │
└─────────────────┘                                   │
```

## Ticket State Machine

```
         ┌──────────────────────────────────────┐
         │                                      │
         ▼                                      │
      ┌──────┐     ┌─────────┐     ┌────────────┴──┐
 ──>  │ OPEN │────>│ TRIAGED │────>│ IN_PROGRESS   │
      └──┬───┘     └────┬────┘     └───┬───────────┘
         │              │             │      ▲
         │              │             ▼      │
         │              │         ┌──────────┴──┐
         │              │         │  RESOLVED    │
         │              │         └──────┬──────┘
         │              │                │
         ▼              ▼                ▼
      ┌──────────────────────────────────────┐
      │              CLOSED                   │
      └──────────────────────────────────────┘
```

### Valid Transitions

| From | Allowed Targets |
|------|----------------|
| `open` | `triaged`, `closed` |
| `triaged` | `in_progress`, `closed` |
| `in_progress` | `resolved`, `triaged` |
| `resolved` | `closed`, `in_progress` |
| `closed` | `open` (reopen) |

Transitions are enforced in `Ticket.transition_to()` (`backend/tickets/models.py`). Invalid transitions raise `InvalidTransitionError`.

## Models Reference

### Ticket (`tickets.models.Ticket`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key, auto-generated |
| `subject` | CharField(200) | Ticket title |
| `body` | TextField | Full description |
| `contact_email` | EmailField | Reporter's email |
| `status` | CharField(20) | One of: open, triaged, in_progress, resolved, closed |
| `priority` | CharField(20) | Nullable. One of: low, medium, high, critical |
| `version` | PositiveInteger | Optimistic concurrency control |
| `created_at` | DateTime | Auto-set on creation |
| `updated_at` | DateTime | Auto-set on save |

### Comment (`tickets.models.Comment`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `ticket` | FK(Ticket) | CASCADE on delete |
| `body` | TextField | Comment content |
| `author_name` | CharField(100) | Who wrote it |
| `created_at` | DateTime | Auto-set |

### Classification (`triage.models.Classification`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `ticket` | OneToOne(Ticket) | CASCADE on delete |
| `category` | CharField(100) | LLM-assigned category |
| `priority_suggestion` | CharField(20) | LLM-suggested priority |
| `sentiment` | CharField(20) | Detected sentiment |
| `confidence` | Float | Classification confidence (0-1) |
| `model_used` | CharField(100) | Which LLM model was used |
| `ticket_version` | PositiveInteger | For idempotency checks |
| `created_at` | DateTime | Auto-set |

### Team (`teams.models.Team`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `name` | CharField(100) | Unique team name |
| `description` | TextField | Optional description |

### TeamMember (`teams.models.TeamMember`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `team` | FK(Team) | CASCADE |
| `user` | FK(User) | Django auth user |
| `role` | CharField(20) | `lead` or `agent` |

Unique constraint: `(team, user)` — a user can only be in a team once.

### RoutingRule (`teams.models.RoutingRule`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `category` | CharField(100) | Matches classification category |
| `priority` | CharField(20) | Optional priority filter (blank = match all) |
| `team` | FK(Team) | Target team |

### Assignment (`teams.models.Assignment`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | UUID | Primary key |
| `ticket_id` | UUID | References ticket (not a FK — loose coupling) |
| `team` | FK(Team) | Assigned team |
| `agent` | FK(TeamMember) | Nullable — optional specific agent |

## Base Models (Shared Kernel)

All domain models inherit from `UUIDModel` (`backend/shared/models.py`), which provides:
- `id` — UUID primary key (auto-generated)
- `created_at` — timestamp set on creation
- `updated_at` — timestamp updated on every save

## Domain Exceptions (`backend/shared/exceptions.py`)

| Exception | When Raised |
|-----------|-------------|
| `DomainException` | Base class for all domain errors |
| `NotFoundError` | Entity not found by ID |
| `InvalidTransitionError` | Invalid ticket status transition |
