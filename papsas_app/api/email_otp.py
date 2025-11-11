import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from papsas_app.models import UserSecurity


class EmailOTPError(Exception):
    def __init__(self, detail, status_code=400, code="email_otp_error", retry_after=None):
        self.detail = detail
        self.status_code = status_code
        self.code = code
        self.retry_after = retry_after


def _salt():
    return (settings.EMAIL_OTP_SECRET_SALT or settings.SECRET_KEY).encode("utf-8")


def _hash_code(user_id, code):
    payload = f"{user_id}:{code}".encode("utf-8")
    return hashlib.sha256(payload + _salt()).hexdigest()


def get_user_security(user):
    security, _ = UserSecurity.objects.get_or_create(user=user)
    return security


def issue_email_otp(user):
    security = get_user_security(user)
    now = timezone.now()
    ttl = timedelta(seconds=settings.EMAIL_OTP_TTL_SECONDS)
    otp = f"{secrets.randbelow(1000000):06d}"
    security.otp_hash = _hash_code(user.id, otp)
    security.otp_expires_at = now + ttl
    security.otp_attempts = 0
    security.otp_locked_until = None
    security.otp_last_sent_at = now
    security.save(
        update_fields=[
            "otp_hash",
            "otp_expires_at",
            "otp_attempts",
            "otp_locked_until",
            "otp_last_sent_at",
        ]
    )
    send_mail(
        subject=f"{settings.SITE_DOMAIN} verification code",
        message=f"Your verification code is {otp}. It expires in {ttl.seconds // 60} minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return security.otp_expires_at


def verify_email_otp(user, code):
    security = get_user_security(user)
    now = timezone.now()
    if security.is_locked():
        retry_after = int((security.otp_locked_until - now).total_seconds())
        raise EmailOTPError("Too many incorrect attempts. Try again later.", status_code=429, retry_after=retry_after)
    if not security.otp_hash or not security.otp_expires_at or security.otp_expires_at < now:
        raise EmailOTPError("Verification code expired.", status_code=400)
    if _hash_code(user.id, code) != security.otp_hash:
        security.otp_attempts += 1
        retry_after = None
        if security.otp_attempts >= settings.EMAIL_OTP_MAX_ATTEMPTS:
            lock_until = now + timedelta(minutes=settings.EMAIL_OTP_LOCK_MINUTES)
            security.otp_locked_until = lock_until
            retry_after = int((lock_until - now).total_seconds())
        security.save(update_fields=["otp_attempts", "otp_locked_until"])
        detail = "Invalid verification code."
        if retry_after:
            raise EmailOTPError(detail, status_code=429, retry_after=retry_after)
        raise EmailOTPError(detail, status_code=400)
    security.email_verified_at = now
    security.clear_otp_state(
        update_fields=[
            "otp_hash",
            "otp_expires_at",
            "otp_attempts",
            "otp_locked_until",
            "otp_last_sent_at",
            "email_verified_at",
        ]
    )
    user.email_verified = True
    user.save(update_fields=["email_verified"])
    return security.email_verified_at
