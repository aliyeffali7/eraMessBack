from django.contrib import admin

from .models import Meeting, MeetingInvite


class MeetingInviteInline(admin.TabularInline):
    model = MeetingInvite
    extra = 0


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ["title", "starts_at", "created_by"]
    inlines = [MeetingInviteInline]
