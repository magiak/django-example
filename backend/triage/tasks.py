import dramatiq
import structlog

logger = structlog.get_logger()


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60000)
def classify_ticket_task(ticket_id: str) -> None:
    """Async task to classify a ticket via LLM. Idempotent."""
    from uuid import UUID

    from .services import classify_ticket

    logger.info("classify_ticket_task.start", ticket_id=ticket_id)
    classification = classify_ticket(ticket_id=UUID(ticket_id))
    logger.info(
        "classify_ticket_task.done",
        ticket_id=ticket_id,
        category=classification.category,
    )
