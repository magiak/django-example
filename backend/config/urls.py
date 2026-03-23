from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from tickets.api import router as tickets_router
from triage.api import router as triage_router
from teams.api import router as teams_router
from knowledge.api import router as knowledge_router

api = NinjaAPI(
    title="Support Ticket Triage",
    version="1.0.0",
    description="AI-powered support ticket triage and routing system",
)

api.add_router("/tickets/", tickets_router)
api.add_router("/triage/", triage_router)
api.add_router("/teams/", teams_router)
api.add_router("/knowledge/", knowledge_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
