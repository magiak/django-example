from django.contrib import admin

from .models import Comment, Ticket


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("id", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "status", "priority", "contact_email", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("subject", "body", "contact_email")
    readonly_fields = ("id", "version", "created_at", "updated_at")
    inlines = [CommentInline]
