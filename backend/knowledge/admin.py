from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "author_name", "created_at")
    list_filter = ("category", "status")
    search_fields = ("title", "content", "author_name")
    readonly_fields = ("id", "created_at", "updated_at")
