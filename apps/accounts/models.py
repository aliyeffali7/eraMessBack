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
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
