# backend-audit-Phase2

## 1. What exists now
- `papsas/settings.py` wires DRF + SimpleJWT, keeps `AUTH_USER_MODEL = "papsas_app.User"`, and already exposes OTP throttling env vars (`OTP_SEND_*`, `OTP_VERIFY_*`). Email credentials live there, but there was no `DEFAULT_FROM_EMAIL` or OTP-specific env for a REST flow yet.
- `papsas_app/models.py` defines the custom `User` (with `email_verified`, `verification_code`, `verification_code_expiration`) and the HTML views (`papsas_app/views.py`) plus `papsas_app/utils/otp_throttle.py` manage otp send/verify throttles for the legacy pages.
- The API surface is split across:
  - `papsas_api` (`/api/auth/*`, `/api/users/me`, `/api/elections/*` via a DRF router).
  - `papsas_app/api` (slashless endpoints for elections, `MeView`, and the legacy web auth).
- No Phase-2-ready email OTP API, `/api/me` patch handler, or dedicated security model existed before this change.

### Endpoints in place today
- From `papsas_api/urls.py`: `GET /api/health`, `POST /api/auth/login`, `POST /api/auth/refresh`, `GET /api/users/me`, and the router-backed `/api/elections/<pk>/` plus `/candidates/` action.
- From `papsas_app/api/urls.py`: `GET /api/health`, `POST /api/auth/login/`, `POST /api/auth/refresh/`, `GET /api/me/`, `GET /api/elections/current`, `/ballot`, `/vote`, `/results`, `/analytics`, `/explain`, `/positions`, `/candidacies`, and the admin `/api/users`.
- The `/api/me` handler and the entire `/auth/email/*` flow are yet to be implemented in this CLI audit (Phase-2 work builds on these existing endpoints).

## 2. Exact files to create/edit

### `papsas_app/models.py`
Add the `UserSecurity` 1-to-1 guard to keep hashed OTP state, lockouts, and `email_verified_at`, keeping user-facing verification near the `User` record.

```python
class UserSecurity(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security",
    )
    email_verified_at = models.DateTimeField(blank=True, null=True)
    otp_hash = models.CharField(max_length=128, blank=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    otp_attempts = models.PositiveSmallIntegerField(default=0)
    otp_locked_until = models.DateTimeField(blank=True, null=True)
    otp_last_sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "user security guard"
        verbose_name_plural = "user security guards"
        ordering = ["user_id"]

    def is_locked(self):
        return bool(self.otp_locked_until and timezone.now() < self.otp_locked_until)

    def clear_otp_state(self, *, update_fields=None):
        self.otp_hash = ""
        self.otp_expires_at = None
        self.otp_attempts = 0
        self.otp_locked_until = None
        self.otp_last_sent_at = None
        self.save(
            update_fields=update_fields
            or [
                "otp_hash",
                "otp_expires_at",
                "otp_attempts",
                "otp_locked_until",
                "otp_last_sent_at",
            ]
        )
```

### `papsas_app/migrations/0096_usersecurity.py`
Create the table and backfill data for existing users via `RunPython`.

```python
migrations.CreateModel(...)
migrations.RunPython(create_user_security, reverse_code=migrations.RunPython.noop)
```

```python
def create_user_security(apps, schema_editor):
    User = apps.get_model("papsas_app", "User")
    UserSecurity = apps.get_model("papsas_app", "UserSecurity")
    for user in User.objects.all():
        UserSecurity.objects.get_or_create(user=user)
```

### `papsas_app/signals.py` & `apps.py`
Hook into `post_save` so brand-new users automatically receive the security row.

### `papsas_app/api/email_otp.py`
Shared OTP helpers do the hashing, throttling, and email delivery for REST clients.

```python
class EmailOTPError(Exception):
    ...

def issue_email_otp(user):
    security = get_user_security(user)
    otp = f"{secrets.randbelow(1000000):06d}"
    security.otp_hash = _hash_code(user.id, otp)
    ...
    send_mail(...)
    return security.otp_expires_at

def verify_email_otp(user, code):
    security = get_user_security(user)
    ...
    if _hash_code(...) != security.otp_hash:
        ...
    security.email_verified_at = now
    security.clear_otp_state(update_fields=[..., "email_verified_at"])
    user.email_verified = True
    user.save(update_fields=["email_verified"])
    return security.email_verified_at
```

### `papsas_app/api/serializers.py`
Extend the user serializer set for `/me`, `/auth/email/start`, and `/auth/email/verify`.

```python
class MeSerializer(ModelSerializer):
    ...

class MeUpdateSerializer(ModelSerializer):
    ...

class EmailVerificationStartSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    def validate_email(...):
        ...

class EmailVerificationVerifySerializer(serializers.Serializer):
    code = serializers.CharField(min_length=6, max_length=6)
```

### `papsas_app/api/views.py`
`MeView` now supports `PATCH` (resets verification when the email changes and triggers an OTP). Add `EmailVerificationStartView`/`EmailVerificationVerifyView` with scoped throttles and consistent responses.

### `papsas_app/api/urls.py`
Register `/auth/email/start`, `/auth/email/verify`, and slashless `/me` along with their trailing-slash aliases.

### `papsas_app/api/permissions.py`
Add the `IsEmailVerified` permission and apply it to admin searches.

### `papsas_app/api/views_user.py`
Use `[IsAdminOnly, IsEmailVerified]` permissions on `/api/users`.

### `papsas/settings.py`
Add:

```python
DEFAULT_FROM_EMAIL = env_str("DEFAULT_FROM_EMAIL", f"no-reply@{SITE_DOMAIN}")
EMAIL_BACKEND = env_str("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")

EMAIL_OTP_TTL_SECONDS = int(env_str("EMAIL_OTP_TTL_SECONDS", "600"))
EMAIL_OTP_SEND_THROTTLE_SECONDS = int(env_str("EMAIL_OTP_SEND_THROTTLE_SECONDS", "60"))
EMAIL_OTP_MAX_ATTEMPTS = int(env_str("EMAIL_OTP_MAX_ATTEMPTS", "5"))
EMAIL_OTP_LOCK_MINUTES = int(env_str("EMAIL_OTP_LOCK_MINUTES", "15"))
EMAIL_OTP_SECRET_SALT = env_str("EMAIL_OTP_SECRET_SALT", "")
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_CLASSES", []).extend([
    "rest_framework.throttling.ScopedRateThrottle",
])
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_RATES", {})
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update({
    "otp_start": "3/min",
    "otp_verify": "10/min",
})
```

### Tests (`papsas_app/tests/test_email_otp.py`)
Add pytest cases covering:

```python
class TestEmailOtpFlow:
    def test_start_happy_path(self, monkeypatch):
        ...
    def test_start_throttled(self):
        ...
    def test_verify_happy_path(self, monkeypatch):
        ...
    def test_verify_max_attempts_locks(self):
        ...
    def test_me_patch_triggers_new_otp(self):
        ...
    def test_admin_endpoint_requires_email_verified(self):
        ...
```

## 3. Settings & env summary
- Add `DEFAULT_FROM_EMAIL`/`EMAIL_BACKEND` so the new API can send emails.
- Introduce OTP env vars: `EMAIL_OTP_TTL_SECONDS`, `EMAIL_OTP_SEND_THROTTLE_SECONDS`, `EMAIL_OTP_MAX_ATTEMPTS`, `EMAIL_OTP_LOCK_MINUTES`, `EMAIL_OTP_SECRET_SALT`.
- Include `ScopedRateThrottle` in DRF defaults and define `otp_start`/`otp_verify` scopes so API throttles match legacy HTML limits.

## 4. Commands to run after applying
1. `python manage.py makemigrations papsas_app`
2. `python manage.py migrate`
3. `python manage.py runserver`

## 5. Branch + commit suggestions
- Branch: `feature/phase2-email-otp`
- Commit message: `Add email OTP verification API and /me patch support`
