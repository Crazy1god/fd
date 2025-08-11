from datetime import timedelta
import logging
import random
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import EmailCode

logger = logging.getLogger("django")
sec_logger = logging.getLogger("django.security")
User = get_user_model()


def generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def create_and_send_code(user: User, purpose: str, template: str, subject: str, ttl_minutes: int = 15) -> EmailCode:
    code = generate_code()
    expires_at = timezone.now() + timedelta(minutes=ttl_minutes)
    ec = EmailCode.objects.create(user=user, purpose=purpose, code=code, expires_at=expires_at)
    body = render_to_string(template, {"code": code, "user": user, "minutes": ttl_minutes})
    send_mail(subject, body, None, [user.email])
    logger.info("Sent %s code to user %s", purpose, user.email)
    return ec


def send_welcome(user: User):
    body = render_to_string("emails/welcome.txt", {"user": user})
    send_mail("Добро пожаловать!", body, None, [user.email])
    logger.info("Sent welcome email to %s", user.email)


def notify_password_changed(user: User):
    body = render_to_string("emails/password_changed.txt", {"user": user})
    send_mail("Пароль изменен", body, None, [user.email])
    logger.info("Sent password changed email to %s", user.email)


def log_suspicious(message: str, **extra):
    sec_logger.warning(message, extra=extra)
