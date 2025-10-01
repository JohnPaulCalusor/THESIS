from pathlib import Path
import os

# --- Paths / env ---
BASE_DIR = Path(__file__).resolve().parent.parent
ENV = os.getenv("DJANGO_ENV", "dev")  # dev | prod

# --- Core ---
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "1" if ENV != "prod" else "0") == "1"

ALLOWED_HOSTS = [h for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o]
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "www.papsasinc.com")

LOGIN_URL = os.getenv("DJANGO_LOGIN_URL", "/login")
AUTH_USER_MODEL = "papsas_app.User"

# --- Core / security driven by env ---
SECURE_PROXY_SSL_HEADER = tuple(os.getenv("SECURE_PROXY_SSL_HEADER", "").split(",")) if os.getenv("SECURE_PROXY_SSL_HEADER") else None
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "0") in {"1", "True", "true", "yes"}
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "0") in {"1", "True", "true", "yes"}

# trust X-Forwarded-Proto when behind Nginx/OLS (only if header is set)
if SECURE_PROXY_SSL_HEADER:
    SECURE_PROXY_SSL_HEADER = (SECURE_PROXY_SSL_HEADER[0], SECURE_PROXY_SSL_HEADER[1])

# --- Apps ---
INSTALLED_APPS = [
    "papsas_app",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_tables2",
    "qrcode",
    "django_crontab",
    # Optional but handy for mobile/web dev
    "corsheaders",
    "rest_framework",
]

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # CORS first among middleware interacting with requests
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

# --- Templates ---
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

# --- Database (single source of truth) ---
if ENV == "prod":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "papsas_db"),
            "USER": os.getenv("POSTGRES_USER", "papsas_user"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "papsas_pass"),
            "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Auth / i18n / tz ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Manila")
USE_I18N = True
# USE_TZ from env (defaults to enabled)
USE_TZ = os.getenv("USE_TZ", "1") in {"1", "True", "true", "yes"}

# --- Static / Media ---
STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles"))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Email ---
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "1") == "1"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

# --- Tables2 ---
DJANGO_TABLES2_TABLE_ATTRS = {"class": "table", "th": {"class": "header-bold"}}

# --- Cron ---
CRONJOBS = [
    ("0 16 * * *", "django.core.management.call_command", ["close_election"]),
    ("0 16 * * *", "django.core.management.call_command", ["check_expiring_memberships"]),
]

# --- OTP throttling defaults ---
OTP_SEND_WINDOW_MINUTES = int(os.getenv("OTP_SEND_WINDOW_MINUTES", "60"))
OTP_SEND_MAX_PER_WINDOW = int(os.getenv("OTP_SEND_MAX_PER_WINDOW", "3"))
OTP_VERIFY_MAX_ATTEMPTS = int(os.getenv("OTP_VERIFY_MAX_ATTEMPTS", "5"))
OTP_LOCK_MINUTES = int(os.getenv("OTP_LOCK_MINUTES", "15"))

# --- CORS (dev helpers; safe defaults) ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:19006",   # Expo
    "http://127.0.0.1:5173",    # Vite
    "http://localhost:5173",
    "http://10.0.2.2:8000",     # Android emulator -> host
]
CORS_ALLOW_CREDENTIALS = True
# ==== ENV PATCH (safe to keep) ===============================================
import os

def _env_bool(name, default=False):
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in ("1","true","yes","on")

def _env_list(name_primary, name_fallback=None, default=""):
    raw = os.getenv(name_primary)
    if not raw and name_fallback:
        raw = os.getenv(name_fallback)
    if raw is None:
        raw = default
    parts = raw.replace(",", " ").split()  # accept comma OR space separated
    return [p.strip() for p in parts if p.strip()]

# Prefer DJANGO_* names, fall back to generic; works with comma or space lists
DEBUG = _env_bool("DJANGO_DEBUG", _env_bool("DEBUG", False))
ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", "ALLOWED_HOSTS", default="localhost 127.0.0.1")
CSRF_TRUSTED_ORIGINS = _env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "CSRF_TRUSTED_ORIGINS", default="")
# ============================================================================ 
