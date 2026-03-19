from datetime import datetime
from uuid import UUID

from ninja import Schema


class TeamOut(Schema):
    id: UUID
    name: str
    description: str
    created_at: datetime


class AssignmentOut(Schema):
    id: UUID
    ticket_id: UUID
    team: TeamOut
    created_at: datetime
