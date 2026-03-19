import dramatiq
import structlog

logger = structlog.get_logger()


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60000)
def route_ticket_task(ticket_id: str, category: str, priority: str) -> None:
    """Async task to route a ticket to the appropriate team after classification."""
    from uuid import UUID

    from .services import route_ticket

    logger.info("route_ticket_task.start", ticket_id=ticket_id)
    assignment = route_ticket(ticket_id=UUID(ticket_id), category=category, priority=priority)
    if assignment:
        logger.info("route_ticket_task.done", ticket_id=ticket_id, team=str(assignment.team))
    else:
        logger.warning("route_ticket_task.no_rule", ticket_id=ticket_id, category=category)
