# -----------------------------------------------------------------------------
# PAPSAS Django settings
#
# Goals:
# - Single source of truth for env values (no duplicate DEBUG assignments)
# - Load .env for local/dev, but never override real environment variables
# - Production toggles come from DJANGO_ENV=prod and DJANGO_* variables
# - Add DRF + SimpleJWT + CORS (env-driven)
# -----------------------------------------------------------------------------

import os
from pathlib import Path
from datetime import timedelta  # <-- for SIMPLE_JWT lifetimes

# ----- Paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env early (if python-dotenv is installed) but DO NOT override exported env
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    load_dotenv = None

if load_dotenv:
    load_dotenv(BASE_DIR / ".env", override=False)

# ----- Small helpers ---------------------------------------------------------
def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

def env_list(name_primary: str, name_fallback: str | None = None, default: str = "") -> list[str]:
    """
    Accept comma OR space separated lists. Prefer DJANGO_* keys but allow fallbacks.
    """
    raw = os.getenv(name_primary)
    if not raw and name_fallback:
        raw = os.getenv(name_fallback)
    if raw is None:
        raw = default
    parts = raw.replace(",", " ").split()
    return [p.strip() for p in parts if p.strip()]

def env_str(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return default if v is None else v

def _env_int(name: str, default: int | None = None) -> int | None:
    v = os.getenv(name)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError:
        return default

# ----- Environment mode ------------------------------------------------------
ENV = env_str("DJANGO_ENV", "dev")  # "dev" | "prod"

# In production, default DEBUG to False unless explicitly set to True via env.
# In dev, default DEBUG to True unless explicitly set to False via env.
DEBUG_DEFAULT = False if ENV == "prod" else True
DEBUG = env_bool("DJANGO_DEBUG", DEBUG_DEFAULT)

# ----- Core security ----------------------------------------------------------
SECRET_KEY = env_str("DJANGO_SECRET_KEY", "dev-insecure-key-change-me")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "ALLOWED_HOSTS", default="localhost 127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "CSRF_TRUSTED_ORIGINS", default="")

SITE_DOMAIN = env_str("SITE_DOMAIN", "www.papsasinc.com")
# ---- Email (env-driven) ---------------------------------------------
import os

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    os.environ.get("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"),
)
# Only used by FileBasedEmailBackend; harmless otherwise
EMAIL_FILE_PATH = os.environ.get("EMAIL_FILE_PATH", "/srv/papsas/var/test-emails")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", f"no-reply@{SITE_DOMAIN}")

LOGIN_URL = env_str("DJANGO_LOGIN_URL", "/login")
AUTH_USER_MODEL = "papsas_app.User"

# If behind a reverse proxy (Nginx), trust X-Forwarded-Proto when configured
_proxy_hdr = env_list("SECURE_PROXY_SSL_HEADER", default="")  # e.g. "HTTP_X_FORWARDED_PROTO https"
SECURE_PROXY_SSL_HEADER = tuple(_proxy_hdr) if len(_proxy_hdr) == 2 else None

# Cookies in prod should be secure
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", ENV == "prod")
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", ENV == "prod")
SESSION_COOKIE_SAMESITE = env_str("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = env_str("CSRF_COOKIE_SAMESITE", "Lax")

# Respect Nginx HTTPS redirect; also allow toggling from env
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", ENV == "prod")

AUDIT_ENABLED = bool(int(os.getenv("AUDIT_ENABLED", "1")))
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "180"))

# (Optional) If you want Django to also emit HSTS (in addition to Nginx),
# uncomment the following three lines. Nginx is already configured to add HSTS.
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# ----- Apps ------------------------------------------------------------------
INSTALLED_APPS = [
    "papsas_app",
    "papsas_app.analytics",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "django_tables2",
    "qrcode",
    "django_crontab",
    "corsheaders",
    "rest_framework",
    # (No need to add 'rest_framework_simplejwt' to INSTALLED_APPS to use its auth class)
]
if DEBUG:
    INSTALLED_APPS.append("django_extensions")
# ----- Middleware -------------------------------------------------------------
MIDDLEWARE = [
    "papsas_app.analytics.middleware.ClientIPMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    # CORS should be early
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "papsas_app.middleware.VisitorCounterMiddleware",
]

ROOT_URLCONF = "papsas.urls"
WSGI_APPLICATION = "papsas.wsgi.application"

# ----- Templates --------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "papsas_app.context_processors.is_officer",
                "papsas_app.context_processors.is_member",
                "papsas_app.context_processors.visitors_count",

                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ----- Database ---------------------------------------------------------------
if ENV == "prod":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env_str("POSTGRES_DB", "papsas_db"),
            "USER": env_str("POSTGRES_USER", "papsas_user"),
            "PASSWORD": env_str("POSTGRES_PASSWORD", "papsas_pass"),
            "HOST": env_str("POSTGRES_HOST", "127.0.0.1"),
            "PORT": env_str("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": int(env_str("POSTGRES_CONN_MAX_AGE", "60")),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ----- Auth / i18n / tz ------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env_str("TIME_ZONE", "Asia/Manila")
USE_I18N = True
USE_TZ = env_bool("USE_TZ", True)

# ----- Static / Media ---------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = env_str("STATIC_ROOT", str(BASE_DIR / "staticfiles"))

MEDIA_URL = "/media/"
MEDIA_ROOT = env_str("MEDIA_ROOT", str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----- Email ------------------------------------------------------------------
EMAIL_HOST = env_str("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(env_str("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = env_str("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env_str("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = env_str("DEFAULT_FROM_EMAIL", f"no-reply@{SITE_DOMAIN}")
EMAIL_BACKEND = env_str("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")

# ----- django-tables2 ---------------------------------------------------------
DJANGO_TABLES2_TABLE_ATTRS = {"class": "table", "th": {"class": "header-bold"}}

# ----- Cron -------------------------------------------------------------------
CRONJOBS = [
    # 4 PM Asia/Manila
    ("0 16 * * *", "django.core.management.call_command", ["close_election"]),
    ("0 16 * * *", "django.core.management.call_command", ["check_expiring_memberships"]),
]

# ----- OTP throttling ---------------------------------------------------------
OTP_SEND_WINDOW_MINUTES = _env_int("OTP_SEND_WINDOW_MINUTES", 60)
OTP_SEND_MAX_PER_WINDOW = _env_int("OTP_SEND_MAX_PER_WINDOW", 3)
OTP_VERIFY_MAX_ATTEMPTS = _env_int("OTP_VERIFY_MAX_ATTEMPTS", 5)
OTP_LOCK_MINUTES = _env_int("OTP_LOCK_MINUTES", 15)
EMAIL_OTP_TTL_SECONDS = _env_int("EMAIL_OTP_TTL_SECONDS", 600)
EMAIL_OTP_SEND_THROTTLE_SECONDS = _env_int("EMAIL_OTP_SEND_THROTTLE_SECONDS", 60)
EMAIL_OTP_MAX_ATTEMPTS = _env_int("EMAIL_OTP_MAX_ATTEMPTS", 5)
EMAIL_OTP_LOCK_MINUTES = _env_int("EMAIL_OTP_LOCK_MINUTES", 15)
EMAIL_OTP_SECRET_SALT = env_str("EMAIL_OTP_SECRET_SALT", "")

# Aliases (OTP_* envs take precedence)
OTP_TTL_MINUTES = _env_int(
    "OTP_TTL_MINUTES",
    max(1, int((EMAIL_OTP_TTL_SECONDS or 600) / 60)),
)
OTP_MAX_ATTEMPTS = _env_int("OTP_MAX_ATTEMPTS", EMAIL_OTP_MAX_ATTEMPTS)
OTP_SEND_THROTTLE_SECONDS = _env_int("OTP_SEND_THROTTLE_SECONDS", EMAIL_OTP_SEND_THROTTLE_SECONDS)
OTP_LOCK_MINUTES = _env_int("OTP_LOCK_MINUTES", EMAIL_OTP_LOCK_MINUTES)

# ----- CORS (env-driven with safe defaults) -----------------------------------
# If you set CORS_ALLOW_ALL_ORIGINS=1, all origins are accepted (dev convenience).
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", False)

# If not allowing all, use the list below (comma/space separated via env)
# Example env:
#   CORS_ALLOWED_ORIGINS="http://localhost:19006 http://127.0.0.1:5173 http://localhost:5173"
_cors_default = "http://localhost:19006 http://127.0.0.1:5173 http://localhost:5173 http://10.0.2.2:8000"
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", default=_cors_default)

# Optional: extend headers if needed by mobile/web clients
CORS_ALLOW_CREDENTIALS = env_bool("CORS_ALLOW_CREDENTIALS", True)
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ----- DRF + JWT --------------------------------------------------------------
REST_FRAMEWORK = {
    # Merge with any existing dict if defined elsewhere
    **globals().get("REST_FRAMEWORK", {}),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # (You can add SessionAuthentication if you also serve server-rendered pages)
        # "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    # Make API responses JSON by default (Browsable API still available if DRF default enabled)
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        # Enable browsable API in dev only
        *(
            ["rest_framework.renderers.BrowsableAPIRenderer"]
            if DEBUG
            else []
        ),
    ],
    "EXCEPTION_HANDLER": "papsas_app.api.exceptions.api_exception_handler",
}

REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_CLASSES", []).extend([
    "rest_framework.throttling.ScopedRateThrottle",
])
REST_FRAMEWORK.setdefault("DEFAULT_THROTTLE_RATES", {})
DRF_THROTTLE_LOGIN = env_str("DRF_THROTTLE_LOGIN", "5/min")
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update({
    "otp_start": "3/min",
    "otp_verify": "10/min",
    "auth_login": DRF_THROTTLE_LOGIN,
})

# >>> PAPSAS v1.4 BEGIN
# Throttle rate for per-user per-election explain endpoint
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update({"explain": "1/min"})
# <<< PAPSAS v1.4 END

# JWT lifetimes are env-driven and align with your /api/auth/login and /api/auth/refresh
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(env_str("JWT_ACCESS_MIN", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(env_str("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": env_bool("JWT_ROTATE_REFRESH_TOKENS", False),
    "BLACKLIST_AFTER_ROTATION": env_bool("JWT_BLACKLIST_AFTER_ROTATION", False),
    "AUTH_HEADER_TYPES": ("Bearer",),
    # If your login returns "access" + "refresh", these defaults are perfect.
}


# --- DRF / JWT add-ons ---
try:
    from .settings_rest import *
except Exception:
    pass
