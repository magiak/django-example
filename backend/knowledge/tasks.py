import dramatiq
import structlog

logger = structlog.get_logger()


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60000)
def generate_tags_task(article_id: str) -> None:
    """Async task to generate tags for an article via LLM. Idempotent."""
    from uuid import UUID

    from .services import generate_tags

    logger.info("generate_tags_task.start", article_id=article_id)
    tags = generate_tags(article_id=UUID(article_id))
    logger.info(
        "generate_tags_task.done",
        article_id=article_id,
        tags=tags,
    )
