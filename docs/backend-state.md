# Backend Audit (2025-11-11 17:25:01 UTC)

- **Endpoints**
  - `POST /api/auth/email/start` (papsas_app/api/views.py:161-189) uses `EmailVerificationStartSerializer` to ensure any supplied email matches the authenticated user, then `issue_email_otp` creates a SHA256 hash stored on `UserSecurity` together with the TTL, attempt counters, lock state, and the last-sent timestamp before sending the code via Django email (papsas_app/api/email_otp.py:34-60 and papsas_app/models.py:136-173).
  - `POST /api/auth/email/verify` (papsas_app/api/views.py:192-210) calls `verify_email_otp`, which guards the code against expiration, compares the salted hash, counts attempts, locks for `EMAIL_OTP_LOCK_MINUTES` once `EMAIL_OTP_MAX_ATTEMPTS` is hit, clears the `UserSecurity` OTP state, and marks `User.email_verified` true when it succeeds.
  - `GET`/`PATCH /api/me` (papsas_app/api/views.py:136-158, papsas_app/api/serializers.py:49-95) return the serialized user info plus `email_verified_at`; PATCH lets the user update first/last name/email, and when the email changes it clears `email_verified`, issues a fresh OTP via `issue_email_otp`, and returns `otp_expires_at` in the response.

- **Throttles**
  - `ScopedRateThrottle` guards both OTP endpoints with the `otp_start` and `otp_verify` scopes, whose limits (`3/min` and `10/min`) live in `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`, complemented by the `EMAIL_OTP_SEND_THROTTLE_SECONDS` cooldown enforced inside `EmailVerificationStartView`. `papsas_app/api/throttles.py` currently only defines `ExplainPerUserElectionThrottle`.

- **Settings**
  - `papsas_app` is the primary app in `INSTALLED_APPS`, which also pulls in Django defaults plus `rest_framework`; DRF uses `JWTAuthentication` via `REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]` (papsas/settings.py). The `.env` file pins `DJANGO_ENV=prod`, so Django tries to use the Postgres block at 127.0.0.1:5432 unless another mode is exported.
  - `OTP_TTL_MINUTES=None`, `OTP_MAX_ATTEMPTS=None`, and `OTP_SEND_THROTTLE_SECONDS=None` in the current environment, while the email OTP feature relies on `EMAIL_OTP_TTL_SECONDS=600`, `EMAIL_OTP_MAX_ATTEMPTS=5`, `EMAIL_OTP_SEND_THROTTLE_SECONDS=60`, and `EMAIL_OTP_LOCK_MINUTES=15` (papsas/settings.py:223-236).
  - Email delivery defaults to `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` and `EMAIL_FILE_PATH=/srv/papsas/var/test-emails`; `/srv/papsas/var/test-emails` exists with `drwxr-xr-x` permissions.

- **Migrations**
  - `python manage.py showmigrations verification` ran with the default `.env` (DJANGO_ENV=prod) and failed with `django.db.utils.OperationalError: connection is bad` because the Postgres server at 127.0.0.1:5432 is not reachable.
  - Re-running the same command with `DJANGO_ENV=dev` switches to SQLite but immediately reports `No installed app with label 'verification'`, since the OTP work actually lives under `papsas_app/api`.

- **Tests**
  - `pytest -q verification` (with `DJANGO_ENV=dev`) cannot start because Python's `tempfile` module throws `FileNotFoundError: No usable temporary directory found in ['/tmp', '/var/tmp', '/usr/tmp', '/srv/papsas/app']`, so the test harness aborts before touching any verification-specific tests.

- **TODOs / risks**
  - Provide a reachable Postgres (or run with `DJANGO_ENV=dev`) if you need to inspect migrations via `showmigrations`; also remember there is no `verification` app directory—look under `papsas_app/api` for the OTP logic.
  - Ensure at least one of the standard temporary directories is writable (or set `TMPDIR` to a writable path) before running pytest or any Django tests, because Python currently cannot create temp files in the sandbox.
