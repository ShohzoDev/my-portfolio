from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Hand-drawn 20x20 stroke icons (currentColor) — no external icon font/CDN needed.
_ICONS = {
    "instagram": (
        '<rect x="3" y="3" width="14" height="14" rx="4"/>'
        '<circle cx="10" cy="10" r="3.3"/>'
        '<circle cx="14.2" cy="5.8" r="0.9" fill="currentColor" stroke="none"/>'
    ),
    "telegram": (
        '<path d="M3 10.4 16.5 4.6c.6-.25 1.15.2.93.95l-2.3 10.4c-.16.75-.6.93-1.22.58'
        'l-3.4-2.5-1.64 1.58c-.18.18-.34.34-.7.34l.25-3.55 6.47-5.85c.28-.25-.06-.4-.44-.15'
        'l-8 5.04-3.45-1.08c-.75-.23-.76-.75.16-1.11Z"/>'
    ),
    "facebook": (
        '<path d="M12.5 3.5h-2A3.5 3.5 0 0 0 7 7v2H5v3h2v6.5h3V12h2.4l.4-3H10V7.2c0-.66.34-1.2 1.2-1.2h1.3Z"/>'
    ),
    "x": ('<path d="M4 4l12 12M16 4 4 16"/>'),
    "linkedin": (
        '<rect x="3" y="3" width="14" height="14" rx="2.5"/>'
        '<circle cx="6.7" cy="7" r="1" fill="currentColor" stroke="none"/>'
        '<path d="M6.7 9.5v5.2M10 9.5v5.2m0-3c0-1.4 1-2.2 2.1-2.2 1.2 0 1.9.8 1.9 2.3v2.9"/>'
    ),
    "youtube": (
        '<rect x="2.5" y="5.5" width="15" height="9" rx="3"/>'
        '<path d="m8.3 8.6 4 1.9-4 1.9Z" fill="currentColor" stroke="none"/>'
    ),
    "github": (
        '<path fill="currentColor" stroke="none" d="M10 2.08a7.92 7.92 0 0 0-2.51 15.44c.4.07.54-.17.54-.38'
        ' 0-.19-.01-.81-.01-1.48-2 .37-2.5-.49-2.67-.93-.09-.23-.48-.93-.81-1.12-.28-.15-.68-.52-.01-.53'
        '.63-.01 1.08.58 1.23.82.72 1.2 1.86.86 2.31.66.07-.52.28-.86.51-1.06-1.77-.2-3.62-.88-3.62-3.92'
        ' 0-.87.31-1.58.82-2.13-.08-.2-.36-1.01.08-2.11 0 0 .67-.21 2.19.82a7.55 7.55 0 0 1 3.98 0'
        'c1.52-1.03 2.19-.82 2.19-.82.44 1.1.16 1.91.08 2.11.51.55.82 1.26.82 2.13 0 3.05-1.86 3.72'
        '-3.63 3.92.29.25.54.72.54 1.47 0 1.06-.01 1.92-.01 2.18 0 .21.14.46.55.38A7.92 7.92 0 0 0 10 2.08Z"/>'
    ),
    "other": (
        '<circle cx="10" cy="10" r="7.5"/>'
        '<path d="M10 2.5c2 2.2 3 4.8 3 7.5s-1 5.3-3 7.5c-2-2.2-3-4.8-3-7.5s1-5.3 3-7.5ZM3 10h14"/>'
    ),
}


@register.simple_tag
def social_icon(platform):
    path = _ICONS.get(platform, _ICONS["other"])
    svg = (
        '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" '
        'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false" '
        'xmlns="http://www.w3.org/2000/svg">' + path + "</svg>"
    )
    return mark_safe(svg)
