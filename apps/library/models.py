from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

MIN_DEGREE = 1
MAX_DEGREE = 33


class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="library/", validators=[FileExtensionValidator(["pdf"])])
    min_degree = models.PositiveSmallIntegerField(
        default=MIN_DEGREE,
        validators=[MinValueValidator(MIN_DEGREE), MaxValueValidator(MAX_DEGREE)],
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploaded_documents"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["min_degree", "-created_at"]

    def __str__(self):
        return self.title
