from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class MessengerUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Loja", {"fields": ("degree",)}),)
    list_display = ["username", "first_name", "last_name", "degree", "is_staff"]
    list_filter = ["is_staff"]
