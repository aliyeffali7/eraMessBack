from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MIN_DEGREE = 1
MAX_DEGREE = 33


class User(AbstractUser):
    degree = models.PositiveSmallIntegerField(
        default=MIN_DEGREE,
        validators=[MinValueValidator(MIN_DEGREE), MaxValueValidator(MAX_DEGREE)],
    )
    section = models.ForeignKey(
        "org.Section", on_delete=models.SET_NULL, null=True, blank=True, related_name="members"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    public_key = models.TextField(
        blank=True,
        default="",
        help_text="Base64 Curve25519 public key for end-to-end encrypted direct messages.",
    )

    def __str__(self):
        return self.username
