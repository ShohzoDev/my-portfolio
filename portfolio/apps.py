from django.apps import AppConfig
from django.conf import settings
from django.core import checks


class PortfolioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portfolio"
    verbose_name = "Portfolio"

    def ready(self):
        from . import security  # noqa: F401 — registers the login-failure signal


@checks.register(checks.Tags.security, deploy=True)
def contact_email_configured(app_configs, **kwargs):
    """Warn before deploying with the placeholder contact address."""
    if not settings.DEBUG and settings.SITE_CONTACT_EMAIL.endswith("@example.com"):
        return [
            checks.Warning(
                "SITE_CONTACT_EMAIL is still the placeholder; the e-mail block is hidden on the site.",
                hint="Set SITE_CONTACT_EMAIL in .env.",
                id="portfolio.W001",
            )
        ]
    return []
