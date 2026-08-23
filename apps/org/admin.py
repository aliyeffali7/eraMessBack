from django.contrib import admin

from .models import Section, Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "created_at"]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ["name", "unit", "created_by", "created_at"]
    list_filter = ["unit"]
