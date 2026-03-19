from datetime import datetime
from uuid import UUID

from ninja import Schema


class ClassificationOut(Schema):
    id: UUID
    ticket_id: UUID
    category: str
    priority_suggestion: str
    sentiment: str
    confidence: float
    model_used: str
    created_at: datetime
