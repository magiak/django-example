from datetime import datetime
from uuid import UUID

from ninja import FilterSchema, Schema


class TicketIn(Schema):
    subject: str
    body: str
    contact_email: str


class TicketStatusIn(Schema):
    status: str


class CommentIn(Schema):
    body: str
    author_name: str


class CommentOut(Schema):
    id: UUID
    body: str
    author_name: str
    created_at: datetime


class TicketOut(Schema):
    id: UUID
    subject: str
    status: str
    priority: str | None
    created_at: datetime
    updated_at: datetime


class TicketDetailOut(Schema):
    id: UUID
    subject: str
    body: str
    contact_email: str
    status: str
    priority: str | None
    version: int
    created_at: datetime
    updated_at: datetime
    comments: list[CommentOut]


class TicketFilters(FilterSchema):
    status: str | None = None
    priority: str | None = None
