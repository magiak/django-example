from uuid import UUID

from django.db import transaction

from shared.exceptions import NotFoundError

from .models import Article


def create_article(*, title: str, content: str, category: str, tags: list[str], author_name: str) -> Article:
    """Create a new article."""
    article = Article.objects.create(
        title=title,
        content=content,
        category=category,
        tags=tags,
        author_name=author_name,
    )
    # Trigger async tag generation if no tags provided
    if not tags:
        from .tasks import generate_tags_task
        generate_tags_task.send(str(article.id))
    return article

def get_article(*, article_id: UUID) -> Article:
    """Retrieve an article by ID or raise NotFoundError."""
    try:
        return Article.objects.get(id=article_id)
    except Article.DoesNotExist:
        raise NotFoundError("Article", str(article_id))

def list_articles(*, category: str | None = None) -> list[Article]:
    """List articles with optional category filter."""
    qs = Article.objects.all()
    if category:
        qs = qs.filter(category=category)
    return list(qs)


def update_article(*, article_id: UUID, title: str, content: str, category: str, tags: list[str]) -> Article:
    """Update an existing article."""
    article = get_article(article_id=article_id)
    article.title = title
    article.content = content
    article.category = category
    article.tags = tags
    article.save()
    return article


def delete_article(*, article_id: UUID) -> None:
    """Delete an article."""
    article = get_article(article_id=article_id)
    article.delete()


@transaction.atomic
def transition_article(*, article_id: UUID, new_status: str) -> Article:
    """Transition article status."""
    try:
        article = Article.objects.select_for_update().get(id=article_id)
    except Article.DoesNotExist:
        raise NotFoundError("Article", str(article_id))
    article.transition_to(new_status)
    article.save()
    return article

def generate_tags(*, article_id: UUID) -> list[str]:
    """Generate tags for an article via LLM."""
    article = get_article(article_id=article_id)

    # If there are any existing tags, skip generation to avoid overwriting human-curated tags
    if article.tags:
        return article.tags

    # Placeholder for LLM integration to generate tags based on article content
    # In a real implementation, this would call an external service or library
    generated_tags = ["example-tag1", "example-tag2"]  # Dummy tags for illustration
    article.tags = generated_tags
    article.save()
    return generated_tags