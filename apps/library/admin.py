from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "min_degree", "uploaded_by", "created_at"]
    list_filter = ["min_degree"]
