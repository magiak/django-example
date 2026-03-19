from django.contrib import admin

from .models import Classification


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("ticket", "category", "priority_suggestion", "sentiment", "confidence", "created_at")
    list_filter = ("category", "sentiment")
    readonly_fields = ("id", "created_at", "updated_at")
