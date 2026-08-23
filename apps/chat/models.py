from django.conf import settings
from django.db import models


class Conversation(models.Model):
    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=120, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversations")
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="admin_of_conversations", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Conversation {self.pk}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender_id}: {self.text[:30]}"
