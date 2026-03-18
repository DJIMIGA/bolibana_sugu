from django.conf import settings
from django.db import models


class PushToken(models.Model):
    DEVICE_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_tokens',
    )
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.email} - {self.device_type} ({'actif' if self.is_active else 'inactif'})"
