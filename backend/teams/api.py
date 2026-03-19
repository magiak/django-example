from uuid import UUID

from ninja import Router

from . import services
from .schemas import AssignmentOut, TeamOut

router = Router(tags=["Teams"])


@router.get("/", response=list[TeamOut])
def list_teams(request):
    return services.list_teams()


@router.get("/assignments/{ticket_id}", response={200: AssignmentOut, 404: dict})
def get_assignment(request, ticket_id: UUID):
    assignment = services.get_assignment(ticket_id=ticket_id)
    if not assignment:
        return 404, {"detail": "No assignment found for this ticket"}
    return assignment
