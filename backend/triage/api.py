from uuid import UUID

from ninja import Router

from shared.exceptions import NotFoundError

from . import services
from .schemas import ClassificationOut

router = Router(tags=["Triage"])


@router.get("/{ticket_id}/classification", response={200: ClassificationOut, 404: dict})
def get_classification(request, ticket_id: UUID):
    try:
        return services.get_classification(ticket_id=ticket_id)
    except NotFoundError as e:
        return 404, {"detail": e.message}
