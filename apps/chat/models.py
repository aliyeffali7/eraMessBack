from django.conf import settings
from django.db import models


class Conversation(models.Model):
    is_group = models.BooleanField(default=False)
    name = models.CharField(max_length=120, blank=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="conversations"
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="admin_of_conversations", blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    # When True (groups only), only admins may post. Toggled by any group admin.
    admins_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or f"Conversation {self.pk}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages"
    )
    # Group messages (not yet E2EE): stored as plaintext here.
    text = models.TextField(blank=True, default="")
    # Direct (1:1) messages: end-to-end encrypted. The server stores only
    # ciphertext + nonce and cannot read the content — decryption happens
    # entirely on the recipient's device using their private key.
    ciphertext = models.TextField(blank=True, default="")
    nonce = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    # Set when the sender edits the message; null otherwise.
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.sender_id}: {'<encrypted>' if self.ciphertext else self.text[:30]}"
        )


class ReadMarker(models.Model):
    """Tracks the last time a given user read a given conversation, so we can
    compute per-user unread counts (WhatsApp-style unread indicator)."""

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="read_markers"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="read_markers"
    )
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("conversation", "user")

    def __str__(self):
        return f"{self.user_id} read {self.conversation_id} @ {self.last_read_at}"
