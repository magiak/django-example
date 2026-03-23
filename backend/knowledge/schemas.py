from datetime import datetime
from uuid import UUID

from ninja import Schema


class ArticleIn(Schema):
    title: str
    content: str
    category: str
    tags: list[str] = []
    author_name: str


class ArticleUpdateIn(Schema):
    title: str
    content: str
    category: str
    tags: list[str] = []


class ArticleStatusIn(Schema):
    status: str


class ArticleOut(Schema):
    id: UUID
    title: str
    category: str
    tags: list[str]
    status: str
    author_name: str
    created_at: datetime
    updated_at: datetime


class ArticleDetailOut(Schema):
    id: UUID
    title: str
    content: str
    category: str
    tags: list[str]
    status: str
    author_name: str
    created_at: datetime
    updated_at: datetime
