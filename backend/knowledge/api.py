from uuid import UUID

from ninja import Router

from shared.exceptions import DomainException, NotFoundError

from . import services
from .schemas import (
    ArticleDetailOut,
    ArticleIn,
    ArticleOut,
    ArticleStatusIn,
    ArticleUpdateIn,
)

router = Router(tags=["Articles"])


@router.post("/", response={201: ArticleOut})
def create_article(request, payload: ArticleIn):
    article = services.create_article(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        tags=payload.tags,
        author_name=payload.author_name,
    )
    return 201, article


@router.get("/", response=list[ArticleOut])
def list_articles(request, category: str | None = None):
    return services.list_articles(category=category)


@router.get("/{article_id}", response={200: ArticleDetailOut, 404: dict})
def get_article(request, article_id: UUID):
    try:
        return services.get_article(article_id=article_id)
    except NotFoundError as e:
        return 404, {"detail": e.message}


@router.put("/{article_id}", response={200: ArticleDetailOut, 404: dict})
def update_article(request, article_id: UUID, payload: ArticleUpdateIn):
    try:
        article = services.update_article(
            article_id=article_id,
            title=payload.title,
            content=payload.content,
            category=payload.category,
            tags=payload.tags,
        )
        return article
    except NotFoundError as e:
        return 404, {"detail": e.message}


@router.patch("/{article_id}/status", response={200: ArticleOut, 400: dict, 404: dict})
def update_article_status(request, article_id: UUID, payload: ArticleStatusIn):
    try:
        article = services.transition_article(article_id=article_id, new_status=payload.status)
        return article
    except NotFoundError as e:
        return 404, {"detail": e.message}
    except DomainException as e:
        return 400, {"detail": e.message}


@router.delete("/{article_id}", response={204: None, 404: dict})
def delete_article(request, article_id: UUID):
    try:
        services.delete_article(article_id=article_id)
        return 204, None
    except NotFoundError as e:
        return 404, {"detail": e.message}
