import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.cache import patch_vary_headers
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET

from .content import DEFAULT_LANGUAGE, LANGUAGE_NAMES, OG_LOCALES, STACK, STRINGS, SUPPORTED_LANGUAGES
from .models import Project, SiteProfile, SocialLink

LANG_COOKIE = "site_lang"

# Line icons for the four services (business systems, SaaS, bots, servers).
SERVICE_ICONS = [
    mark_safe(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round" focusable="false">'
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><path d="M14 17.5h7M17.5 14v7"/></svg>'
    ),
    mark_safe(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round" focusable="false">'
        '<path d="M12 3 3 7.5l9 4.5 9-4.5L12 3Z"/><path d="m3 12 9 4.5 9-4.5"/><path d="m3 16.5 9 4.5 9-4.5"/></svg>'
    ),
    mark_safe(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round" focusable="false">'
        '<path d="M21 4 3 11l6.5 2.5L12 20l3-4.5L21 4Z"/><path d="m9.5 13.5 5-4"/></svg>'
    ),
    mark_safe(
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round" focusable="false">'
        '<rect x="3" y="4" width="18" height="7" rx="1.5"/><rect x="3" y="13" width="18" height="7" rx="1.5"/><path d="M7 7.5h.01M7 16.5h.01M11 7.5h6M11 16.5h6"/></svg>'
    ),
]
LANG_COOKIE_MAX_AGE = 60 * 60 * 24 * 365


# ---------------------------------------------------------------------------
# Language resolution
# ---------------------------------------------------------------------------

def _accept_language_codes(header):
    """Language codes from an Accept-Language header, best first."""
    weighted = []
    for i, part in enumerate(header.split(",")):
        piece = part.strip()
        if not piece:
            continue
        code, _, params = piece.partition(";")
        q = 1.0
        if params.strip().startswith("q="):
            try:
                q = float(params.strip()[2:])
            except ValueError:
                q = 0.0
        weighted.append((-q, i, code.strip().split("-")[0].lower()))
    return [code for _, _, code in sorted(weighted)]


def preferred_language(request):
    """Cookie (an explicit earlier choice) wins, then the browser's languages."""
    cookie = request.COOKIES.get(LANG_COOKIE)
    if cookie in SUPPORTED_LANGUAGES:
        return cookie
    for code in _accept_language_codes(request.META.get("HTTP_ACCEPT_LANGUAGE", "")):
        if code in SUPPORTED_LANGUAGES:
            return code
    return DEFAULT_LANGUAGE


@require_GET
def root_redirect(request):
    """`/` → `/uz/`, `/ru/` or `/en/`. Each language has its own URL so search
    engines can index all three (they don't send cookies)."""
    response = HttpResponseRedirect(f"/{preferred_language(request)}/")
    patch_vary_headers(response, ("Cookie", "Accept-Language"))
    return response


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

def _json_for_script(data):
    """JSON safe to inline in a <script> tag (same escaping as json_script)."""
    text = json.dumps(data, ensure_ascii=False)
    return mark_safe(
        text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    )


def _abs_static(request, path):
    # A plain STATIC_URL join instead of static(): WhiteNoise's manifest
    # storage raises for a missing manifest entry, which must never 500 the
    # homepage over a share-preview image.
    return request.build_absolute_uri(f"{settings.STATIC_URL}{path}")


def _public_email():
    """The contact address, or "" while it is still the placeholder."""
    email = settings.SITE_CONTACT_EMAIL
    return "" if email.endswith("@example.com") else email


def _asset_version():
    """Changes whenever style.css or site.js changes, so the browser never
    pairs fresh HTML with a stale cached stylesheet (production also has
    WhiteNoise's hashed file names; this matters most under runserver)."""
    stamps = []
    for name in ("css/style.css", "js/site.js"):
        try:
            stamps.append(int((settings.BASE_DIR / "static" / "portfolio" / name).stat().st_mtime))
        except OSError:
            pass
    return max(stamps, default=0)


def _projects(lang):
    strings = STRINGS[lang]
    projects = [p.localized(lang) for p in Project.objects.filter(is_active=True)]
    for p in projects:
        p["status_label"] = strings[f"status_{p['status']}"]
    return projects


def _person(request, lang, profile, strings, social_links, github_url, email):
    """schema.org Person for search engines."""
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile.full_name,
        "jobTitle": strings["hero_role"],
        "description": strings["hero_tagline"],
        "url": request.build_absolute_uri(f"/{lang}/"),
        "image": _abs_static(request, "portfolio/img/profile-800.jpg"),
        "address": {"@type": "PostalAddress", "addressCountry": "UZ"},
        "knowsLanguage": ["uz", "ru", "en"],
        "knowsAbout": STACK,
        "sameAs": [github_url] + [s.url for s in social_links if s.url != github_url],
    }
    if profile.full_name_ru and profile.full_name_ru != profile.full_name:
        person["alternateName"] = profile.full_name_ru
    if email:
        person["email"] = f"mailto:{email}"
    return person


def _remember_language(response, lang):
    response.set_cookie(LANG_COOKIE, lang, max_age=LANG_COOKIE_MAX_AGE, samesite="Lax")
    return response


@require_GET
def index(request, lang):
    strings = STRINGS[lang]
    profile = SiteProfile.load()
    social_links = [s for s in SocialLink.objects.filter(is_active=True) if s.has_link]
    telegram_url = next((s.url for s in social_links if s.platform == SocialLink.Platform.TELEGRAM), "")
    github_url = f"https://github.com/{settings.SITE_GITHUB_USERNAME}"
    email = _public_email()
    display_name = profile.name_for(lang)
    page_title = f"{display_name} — {strings['hero_role']}"

    context = {
        "lang": lang,
        "strings": strings,
        "profile": profile,
        "projects": _projects(lang),
        "services": [
            {"icon": SERVICE_ICONS[i - 1], "title": strings[f"s{i}_t"], "desc": strings[f"s{i}_d"]}
            for i in range(1, 5)
        ],
        "code_stack": STACK[:3],
        "code_builds": json.loads(strings["code_builds"]),
        "stack": STACK,
        "social_links": social_links,
        "telegram_url": telegram_url,
        "contact_email": email,
        "social_handle": settings.SITE_SOCIAL_HANDLE,
        "page_title": page_title,
        "display_name": display_name,
        "process": [{"n": f"0{i}", "title": strings[f"p{i}_t"], "desc": strings[f"p{i}_d"]} for i in range(1, 5)],
        "page_description": strings["hero_tagline"],
        "canonical_url": request.build_absolute_uri(f"/{lang}/"),
        "alternates": [
            {"code": code, "name": LANGUAGE_NAMES[code], "path": f"/{code}/",
             "url": request.build_absolute_uri(f"/{code}/")}
            for code in SUPPORTED_LANGUAGES
        ],
        "x_default_url": request.build_absolute_uri("/"),
        "og_image_url": _abs_static(request, "portfolio/img/og-image.jpg"),
        "og_locale": OG_LOCALES[lang],
        "og_locale_alternates": [OG_LOCALES[c] for c in SUPPORTED_LANGUAGES if c != lang],
        "asset_version": _asset_version(),
        "jsonld": _json_for_script(
            _person(request, lang, profile, strings, social_links, github_url, email)
        ),
    }
    return _remember_language(render(request, "portfolio/index.html", context), lang)


# ---------------------------------------------------------------------------
# SEO plumbing
# ---------------------------------------------------------------------------

@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


@require_GET
def sitemap_xml(request):
    """The home page in 3 languages, each listing the others via hreflang."""
    urls = {code: request.build_absolute_uri(f"/{code}/") for code in SUPPORTED_LANGUAGES}
    alternates = "".join(
        f'    <xhtml:link rel="alternate" hreflang="{code}" href="{url}"/>\n' for code, url in urls.items()
    )
    alternates += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{request.build_absolute_uri("/")}"/>\n'
    entries = "".join(
        f"  <url>\n    <loc>{url}</loc>\n{alternates}    <changefreq>monthly</changefreq>\n  </url>\n"
        for url in urls.values()
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{entries}</urlset>\n"
    )
    return HttpResponse(xml, content_type="application/xml")
