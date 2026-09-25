from django.conf import settings
from django.db import models


class Meeting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return self.title


class MeetingInvite(models.Model):
    PENDING = "pending"
    YES = "yes"
    NO = "no"
    RESPONSE_CHOICES = [(PENDING, "Gözləyir"), (YES, "Bəli"), (NO, "Xeyr")]

    meeting = models.ForeignKey(
        Meeting, on_delete=models.CASCADE, related_name="invites"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="meeting_invites",
    )
    response = models.CharField(
        max_length=10, choices=RESPONSE_CHOICES, default=PENDING
    )
    # Optional explanation given when the invitee answers "no".
    reason = models.CharField(max_length=300, blank=True, default="")

    class Meta:
        unique_together = ("meeting", "user")

    def __str__(self):
        return f"{self.meeting.title} -> {self.user.username}: {self.response}"
