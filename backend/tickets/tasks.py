import dramatiq


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60000)
def on_ticket_created(ticket_id: str) -> None:
    """Triggered when a new ticket is created. Enqueues triage classification."""
    # Will be wired to triage.tasks.classify_ticket_task in Session 2
    pass
