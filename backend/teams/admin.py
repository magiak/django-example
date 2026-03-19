from django.contrib import admin

from .models import Assignment, RoutingRule, Team, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "role")
    list_filter = ("role", "team")


@admin.register(RoutingRule)
class RoutingRuleAdmin(admin.ModelAdmin):
    list_display = ("category", "priority", "team")
    list_filter = ("team",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("ticket_id", "team", "agent", "created_at")
    list_filter = ("team",)
