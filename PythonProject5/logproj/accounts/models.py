from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

    class Meta:
        db_table = 'auth_user'

class Purpose(models.TextChoices):
    REGISTRATION = "registration", "Registration"
    PASSWORD_RESET = "password_reset", "Password reset"


class EmailCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_codes")  # Изменено
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    code = models.CharField(max_length=6, validators=[MinLengthValidator(6)])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "purpose", "code"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])