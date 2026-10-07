"""
Small security pieces shared by the views:

- client IP + its salted hash (rate limits store only the hash),
- admin login throttling (password guessing),
- security response headers incl. Content-Security-Policy.
"""

import base64
import hashlib
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver
from django.http import HttpResponse
from django.utils import timezone

logger = logging.getLogger(__name__)

# The one inline script on the site (adds the `js` class before first paint so
# reveal animations never flash). CSP allows exactly this text via its hash —
# templates/portfolio/base.html must contain it byte-for-byte (a test checks).
JS_FLAG_SCRIPT = 'document.documentElement.classList.add("js")'
JS_FLAG_HASH = "sha256-" + base64.b64encode(hashlib.sha256(JS_FLAG_SCRIPT.encode()).digest()).decode()

CONTENT_SECURITY_POLICY = "; ".join(
    [
        "default-src 'self'",
        f"script-src 'self' '{JS_FLAG_HASH}'",
        "style-src 'self'",
        "img-src 'self' data:",
        "font-src 'self'",
        "connect-src 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "object-src 'none'",
    ]
)
PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"


# ---------------------------------------------------------------------------
# Client identity
# ---------------------------------------------------------------------------

def client_ip(request):
    """Client IP for rate limiting.

    Proxy headers are only trusted when CONTACT_TRUST_PROXY_HEADERS is on
    (i.e. nginx / PythonAnywhere sits in front and sets them). Then we use
    X-Real-IP, or the right-most X-Forwarded-For entry — the one our own
    proxy appended, which the client cannot forge. Otherwise REMOTE_ADDR.
    """
    if settings.CONTACT_TRUST_PROXY_HEADERS:
        real_ip = request.META.get("HTTP_X_REAL_IP", "").strip()
        if real_ip:
            return real_ip
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def ip_hash(ip):
    return hashlib.sha256(f"{settings.SECRET_KEY}:{ip}".encode()).hexdigest()


# ---------------------------------------------------------------------------
# Admin login throttling
# ---------------------------------------------------------------------------

def _recent_failures(hashed):
    from .models import LoginFailure

    since = timezone.now() - timedelta(minutes=settings.ADMIN_LOGIN_WINDOW_MINUTES)
    return LoginFailure.objects.filter(ip_hash=hashed, created_at__gte=since).count()


def _recent_failures_total():
    from .models import LoginFailure

    since = timezone.now() - timedelta(minutes=settings.ADMIN_LOGIN_WINDOW_MINUTES)
    return LoginFailure.objects.filter(created_at__gte=since).count()


def throttled_admin_login(request, extra_context=None):
    """Admin login view that refuses new attempts after too many failures —
    per client, plus a global cap so rotating IPs doesn't help either."""
    if request.method == "POST":
        hashed = ip_hash(client_ip(request))
        if (
            _recent_failures(hashed) >= settings.ADMIN_LOGIN_MAX_FAILURES
            or _recent_failures_total() >= settings.ADMIN_LOGIN_GLOBAL_MAX_FAILURES
        ):
            logger.warning("Admin login throttled for ip_hash=%s…", hashed[:12])
            return HttpResponse(
                "Juda ko'p urinish. Birozdan so'ng qayta urinib ko'ring. / "
                "Too many attempts, try again later.",
                status=429,
                content_type="text/plain; charset=utf-8",
            )
    return admin.site.login(request, extra_context)


@receiver(user_login_failed)
def _record_login_failure(sender, credentials=None, request=None, **kwargs):
    if request is None:
        return
    from .models import LoginFailure

    LoginFailure.objects.create(ip_hash=ip_hash(client_ip(request)))
    # Keep the table tiny: nothing older than a day matters.
    LoginFailure.objects.filter(created_at__lt=timezone.now() - timedelta(days=1)).delete()
    logger.warning("Failed admin login")


# ---------------------------------------------------------------------------
# Headers
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware:
    """CSP + Permissions-Policy on the public site.

    The Django admin is skipped: it relies on inline styles that a strict
    style-src would break, and it is not a public surface anyway.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_prefix = "/" + settings.ADMIN_URL

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG and response.status_code >= 400:
            return response  # Django's debug error pages rely on inline CSS/JS
        if not request.path.startswith(self.admin_prefix):
            response.headers.setdefault("Content-Security-Policy", CONTENT_SECURITY_POLICY)
            response.headers.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        return response
