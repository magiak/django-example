from django.db import models

from shared.exceptions import InvalidTransitionError
from shared.models import UUIDModel


class ArticleStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


VALID_TRANSITIONS = {
    "draft": ["published"],
    "published": ["archived", "draft"],
    "archived": ["draft"],
}


class Article(UUIDModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        db_index=True,
    )
    author_name = models.CharField(max_length=100)

    class Meta:
        # Sort order
        ordering = ["-created_at"]

        # Database indexes
        indexes = [
            models.Index(fields=["category", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"[{self.status}] {self.title}"

    def transition_to(self, new_status: str) -> None:
        allowed = VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise InvalidTransitionError("Article", self.status, new_status)
        self.status = new_status
