from django.conf import settings
from django.db import models


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="announcements",
        limit_choices_to={"role": "admin"},
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
