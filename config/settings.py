"""
Django settings for the shohzodev portfolio project.

Deployment targets (matches the author's usual workflow):
- PythonAnywhere (SQLite)
- Hetzner VPS / any server with nginx + gunicorn (PostgreSQL optional)
- Render

Configuration is driven by environment variables so the same codebase
works unmodified across all of them. See README.md for deploy steps.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env(name, default=""):
    """Read an environment variable, treating a blank value as unset.

    A line like `DJANGO_SECRET_KEY=` in .env yields an *empty string*, not
    a missing variable — with plain os.environ.get(name, default) that empty
    string wins over the default and silently breaks things (an empty
    SECRET_KEY crashes every request, even Django's own error page).
    """
    value = os.environ.get(name, "").strip()
    return value if value else default

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

DEBUG = env("DJANGO_DEBUG", "True") == "True"

_DEV_ONLY_SECRET_KEY = "dev-insecure-secret-key-change-me-in-production"
SECRET_KEY = env("DJANGO_SECRET_KEY", _DEV_ONLY_SECRET_KEY)

if not DEBUG and SECRET_KEY == _DEV_ONLY_SECRET_KEY:
    # Refuse to run in production with the throwaway dev key — this is
    # exactly the kind of mistake ("forgot to set an env var") that quietly
    # leaves a site wide open. Generate a real one, e.g.:
    #   python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY muhit o'zgaruvchisi o'rnatilmagan. DEBUG=False bilan "
        "standart (dev) kalitdan foydalanish xavfsiz emas — production uchun "
        "yangi tasodifiy kalit generatsiya qiling va uni DJANGO_SECRET_KEY ga "
        "o'rnating (qarang: README.md)."
    )

ALLOWED_HOSTS = [
    h.strip()
    for h in env("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in env("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portfolio",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "portfolio.security.SecurityHeadersMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Defaults to SQLite (works out of the box on PythonAnywhere). Set
# DATABASE_URL-style env vars below to switch to PostgreSQL on a VPS.

if env("POSTGRES_DB"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB"),
            "USER": env("POSTGRES_USER", "postgres"),
            "PASSWORD": env("POSTGRES_PASSWORD", ""),
            "HOST": env("POSTGRES_HOST", "localhost"),
            "PORT": env("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    # Must be listed explicitly: defining STORAGES replaces Django's default
    # dict, and without "default" every media upload (project covers) fails.
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Site content (edit these, or move to the DB later if it grows)
# ---------------------------------------------------------------------------

SITE_OWNER_NAME = "Shohzod"
# Intentionally NOT hardcoded here: a personal email baked into settings.py
# ends up permanently in git history the moment this repo goes public (e.g.
# on GitHub, like your other projects). Put the real address in your local
# .env (gitignored) — see .env.example.
SITE_CONTACT_EMAIL = env("SITE_CONTACT_EMAIL", "contact@example.com")
SITE_GITHUB_USERNAME = "ShohzoDev0108"

# Contact form → Telegram. Optional: if either value is empty, messages are
# still saved and visible in the admin panel, just not pushed to Telegram.
#   TELEGRAM_BOT_TOKEN — from @BotFather
#   TELEGRAM_CHAT_ID   — your own chat id (e.g. from @userinfobot)
TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID", "")

# Anti-spam: max contact-form messages per sender per hour, plus a global cap
# so a bot rotating IPs still can't flood the inbox / Telegram.
CONTACT_RATE_LIMIT_PER_HOUR = int(env("CONTACT_RATE_LIMIT_PER_HOUR", "5"))
CONTACT_GLOBAL_LIMIT_PER_HOUR = int(env("CONTACT_GLOBAL_LIMIT_PER_HOUR", "30"))
# Only trust X-Real-IP / X-Forwarded-For when a proxy you control (nginx,
# PythonAnywhere) sets them. Without a proxy, anyone can forge these headers
# to dodge the per-sender limit — so the default is to use REMOTE_ADDR.
CONTACT_TRUST_PROXY_HEADERS = env("CONTACT_TRUST_PROXY_HEADERS", "False") == "True"

# ---------------------------------------------------------------------------
# Admin panel
# ---------------------------------------------------------------------------

# A non-default admin path (set DJANGO_ADMIN_URL in .env, e.g. "boshqaruv-7f3k/")
# keeps bots that hammer /admin/ away from the login form. Not secret-grade —
# the login throttle below is the real protection.
ADMIN_URL = env("DJANGO_ADMIN_URL", "admin/").strip("/") + "/"
ADMIN_LOGIN_MAX_FAILURES = int(env("ADMIN_LOGIN_MAX_FAILURES", "5"))
ADMIN_LOGIN_WINDOW_MINUTES = int(env("ADMIN_LOGIN_WINDOW_MINUTES", "15"))
# Failed logins from all clients together within the window before the login
# form pauses for everyone (stops IP-rotating guessing).
ADMIN_LOGIN_GLOBAL_MAX_FAILURES = int(env("ADMIN_LOGIN_GLOBAL_MAX_FAILURES", "30"))
# Note: the client IP comes from portfolio.security.client_ip — behind nginx
# set CONTACT_TRUST_PROXY_HEADERS=True, or every visitor looks like 127.0.0.1.

# ---------------------------------------------------------------------------
# Logging — errors go to stderr, which gunicorn/systemd (journalctl) and
# PythonAnywhere's error log capture. Without this, a production 500 or a
# failed Telegram notification would leave no trace at all.
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "stderr": {"class": "logging.StreamHandler", "formatter": "plain"},
    },
    "root": {"handlers": ["stderr"], "level": "WARNING"},
    "loggers": {
        "django.request": {"handlers": ["stderr"], "level": "ERROR", "propagate": False},
        "portfolio": {"handlers": ["stderr"], "level": "INFO", "propagate": False},
    },
}

# ---------------------------------------------------------------------------
# Production hardening (only active when DEBUG=False)
# ---------------------------------------------------------------------------

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = env("DJANGO_SECURE_SSL_REDIRECT", "True") == "True"
    # Start conservative (1 hour) and raise once HTTPS is confirmed solid on
    # the real domain — a wrong HSTS value is hard to undo for visitors who
    # already cached it.
    SECURE_HSTS_SECONDS = int(env("DJANGO_HSTS_SECONDS", "3600"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    X_FRAME_OPTIONS = "DENY"
