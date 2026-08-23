from django.conf import settings
from django.db import models

from apps.chat.models import Conversation


class Unit(models.Model):
    name = models.CharField(max_length=150)
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name="unit")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Section(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=150)
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name="section")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["unit__name", "name"]

    def __str__(self):
        return f"{self.unit.name} / {self.name}"
