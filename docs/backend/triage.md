# Triage — Bounded Context

**Location:** `backend/triage/`

## Purpose

The triage context receives a ticket ID, calls an LLM to classify it (category, priority, sentiment), and stores the result. This is the integration boundary with external AI services.

## Domain Concepts

- **Classification** — the AI-generated analysis of a ticket
- **Idempotency** — if a classification already exists for the current ticket version, processing is skipped
- **Async Processing** — classification runs as a Dramatiq background task to avoid blocking the API

## Model

### Classification

```python
class Classification(UUIDModel):
    ticket: OneToOneField(Ticket)
    category: CharField(100)          # e.g., "authentication", "billing", "general_inquiry"
    priority_suggestion: CharField(20) # e.g., "high", "medium"
    sentiment: CharField(20)          # e.g., "frustrated", "neutral", "positive"
    confidence: FloatField            # 0.0 to 1.0
    model_used: CharField(100)        # e.g., "gpt-4", "claude-3"
    ticket_version: PositiveIntegerField  # idempotency: matches Ticket.version
```

## Services (`services.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_classification` | `(ticket_id) -> Classification` | Returns classification, raises `NotFoundError` |
| `classify_ticket` | `(ticket_id) -> Classification` | Runs LLM classification (idempotent) |

### Idempotency

`classify_ticket()` checks if a `Classification` already exists for the ticket's current `version`. If it does, the existing classification is returned without calling the LLM. This prevents duplicate processing when Dramatiq retries a task.

```python
# Idempotency check
existing = Classification.objects.filter(ticket=ticket, ticket_version=ticket.version).first()
if existing:
    return existing  # skip LLM call
```

## Tasks (`tasks.py`)

### `classify_ticket_task`

```python
@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60000)
def classify_ticket_task(ticket_id: str) -> None:
```

- Receives ticket ID as a string (primitives only — Dramatiq serialization)
- Calls `services.classify_ticket()` which handles idempotency
- Retries up to 3 times with exponential backoff (1s → 60s)
- Logs start and completion with structlog

## API Endpoints

| Method | Path | Response | Status Codes |
|--------|------|----------|-------------|
| `GET` | `/api/triage/{ticket_id}/classification` | `ClassificationOut` | 200, 404 |

## LLM Integration

Currently uses a **mock implementation** that returns hardcoded values:

```python
result = {
    "category": "general_inquiry",
    "priority_suggestion": "medium",
    "sentiment": "neutral",
    "confidence": 0.85,
    "model_used": "mock",
}
```

Future implementation will add:
- `llm_client.py` — thin wrapper around OpenAI/Anthropic SDK
- `prompts.py` — prompt templates for classification
- Structured output parsing (JSON mode)
- Timeout and error handling

## Data Flow

```
Ticket Created
    → tickets.tasks.on_ticket_created(ticket_id)
    → triage.tasks.classify_ticket_task(ticket_id)   [Dramatiq queue]
    → triage.services.classify_ticket(ticket_id)
    → Check idempotency (skip if already classified for this version)
    → Call LLM (currently mock)
    → Save Classification to DB
    → (future) enqueue teams.tasks.route_ticket_task
```
