"""
Push new contact-form messages to Telegram.

Standard library only (urllib) — no extra dependency for one HTTPS call.
A failure here must never break the contact form: the message is already
saved in the database, so we log and move on.
"""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def telegram_enabled():
    return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)


def _escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def notify_new_message(msg):
    """Send `msg` (a ContactMessage) to Telegram. Returns True on success."""
    if not telegram_enabled():
        return False

    text = (
        "📩 <b>Portfolio: yangi xabar</b>\n\n"
        f"<b>Ism:</b> {_escape_html(msg.name)}\n"
        f"<b>Aloqa:</b> {_escape_html(msg.contact)}\n"
        f"<b>Til:</b> {msg.lang.upper() or '—'}\n\n"
        f"{_escape_html(msg.message)}"
    )
    payload = json.dumps(
        {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": text[:4000],
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
    ).encode()
    request = urllib.request.Request(
        TELEGRAM_API.format(token=settings.TELEGRAM_BOT_TOKEN),
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=6) as response:
            body = json.loads(response.read().decode() or "{}")
            if body.get("ok"):
                return True
            logger.warning("Telegram rejected contact notification: %s", body)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        logger.warning("Telegram contact notification failed: %s", exc)
    return False
