import json

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.cache import patch_vary_headers
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST

from .content import (
    DEFAULT_LANGUAGE,
    LANGUAGE_NAMES,
    OG_LOCALES,
    STRINGS,
    SUPPORTED_LANGUAGES,
    localized_skills,
    plural_key,
)
from .forms import ContactForm
from .models import ContactMessage, Project, SocialLink
from .notifications import notify_new_message

LANG_COOKIE = "site_lang"
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


def _build_context(request, lang, form=None, sent=False):
    strings = STRINGS[lang]
    projects = [p.localized(lang) for p in Project.objects.filter(is_active=True)]
    for p in projects:
        p["status_label"] = strings[f"status_{p['status']}"]
    featured = [p for p in projects if p["tier"] == Project.Tier.FEATURED]
    main = [p for p in projects if p["tier"] == Project.Tier.MAIN]
    other = [p for p in projects if p["tier"] == Project.Tier.OTHER]
    live_count = sum(1 for p in projects if p["status"] == Project.Status.LIVE)

    social_links = list(SocialLink.objects.filter(is_active=True))
    github_url = f"https://github.com/{settings.SITE_GITHUB_USERNAME}"
    email = settings.SITE_CONTACT_EMAIL
    skills = localized_skills(lang)

    canonical = request.build_absolute_uri(f"/{lang}/")
    alternates = [
        {"code": code, "name": LANGUAGE_NAMES[code], "url": request.build_absolute_uri(f"/{code}/")}
        for code in SUPPORTED_LANGUAGES
    ]

    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Shohzod",
        "jobTitle": strings["hero_role"],
        "description": strings["hero_tagline"],
        "url": canonical,
        "image": _abs_static(request, "portfolio/img/profile-800.jpg"),
        "address": {"@type": "PostalAddress", "addressCountry": "UZ"},
        "knowsLanguage": ["uz", "ru", "en"],
        "knowsAbout": sorted({tag for group in skills for tag in group["tags"]}),
        "sameAs": [github_url] + [s.url for s in social_links if s.has_link and s.url != github_url],
    }
    if not email.endswith("@example.com"):
        person["email"] = f"mailto:{email}"

    # ⌘K palette entries, already translated — the JS just filters/executes.
    commands = [
        {"group": strings["cmdk_group_nav"], "label": strings[key], "kind": "scroll", "target": target}
        for key, target in (
            ("nav_top", "#top"),
            ("nav_about", "#about"),
            ("nav_skills", "#skills"),
            ("nav_projects", "#projects"),
            ("nav_contact", "#contact"),
        )
    ]
    commands += [
        {"group": strings["cmdk_group_projects"], "label": p["title"], "kind": "scroll", "target": f"#p-{p['slug']}"}
        for p in projects
    ]
    commands += [
        {"group": strings["cmdk_group_actions"], "label": strings["cmdk_copy_email"], "kind": "copy", "value": email},
        {"group": strings["cmdk_group_actions"], "label": strings["contact_email_btn"], "kind": "href", "href": f"mailto:{email}"},
        {"group": strings["cmdk_group_actions"], "label": strings["cmdk_github"], "kind": "href", "href": github_url, "external": True},
    ]
    commands += [
        {
            "group": strings["cmdk_group_lang"],
            "label": alt["name"],
            "kind": "href",
            "href": f"/{alt['code']}/",
            "current": alt["code"] == lang,
        }
        for alt in alternates
    ]

    return {
        "lang": lang,
        "strings": strings,
        "skills": skills,
        "featured_projects": featured,
        "main_projects": main,
        "other_projects": other,
        "live_count": live_count,
        "badge_label": strings[plural_key(lang, live_count)],
        "social_links": social_links,
        "contact_email": email,
        "github_url": github_url,
        "canonical_url": canonical,
        "alternates": alternates,
        "x_default_url": request.build_absolute_uri("/"),
        "og_image_url": _abs_static(request, "portfolio/img/og-image.jpg"),
        "og_locale": OG_LOCALES[lang],
        "og_locale_alternates": [OG_LOCALES[c] for c in SUPPORTED_LANGUAGES if c != lang],
        "person_jsonld": _json_for_script(person),
        "commands": commands,
        "form": form or ContactForm(lang=lang),
        "sent": sent,
    }


def _remember_language(response, lang):
    response.set_cookie(LANG_COOKIE, lang, max_age=LANG_COOKIE_MAX_AGE, samesite="Lax")
    return response


@require_GET
def index(request, lang):
    context = _build_context(request, lang, sent=request.GET.get("sent") == "1")
    return _remember_language(render(request, "portfolio/index.html", context), lang)


# ---------------------------------------------------------------------------
# Contact form
# ---------------------------------------------------------------------------

def _client_ip(request):
    """Best-effort client IP behind nginx / PythonAnywhere.

    X-Real-IP (set by the proxy) first, then the right-most X-Forwarded-For
    entry — the one our own proxy appended, which the client can't forge.
    """
    real_ip = request.META.get("HTTP_X_REAL_IP", "").strip()
    if real_ip:
        return real_ip
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _rate_limited(request):
    key = f"contact-rate:{_client_ip(request)}"
    added = cache.add(key, 1, timeout=60 * 60)
    if added:
        return False
    try:
        count = cache.incr(key)
    except ValueError:  # expired between add() and incr()
        cache.add(key, 1, timeout=60 * 60)
        return False
    return count > settings.CONTACT_RATE_LIMIT_PER_HOUR


@require_POST
def contact_submit(request, lang):
    strings = STRINGS[lang]
    wants_json = request.headers.get("X-Requested-With") == "fetch"
    form = ContactForm(request.POST, lang=lang)
    success_url = reverse("portfolio:index", args=[lang]) + "?sent=1#contact"

    if form.is_spam:
        # Pretend it worked — telling a bot it was caught only teaches it.
        if wants_json:
            return JsonResponse({"ok": True, "message": strings["form_success"]})
        return HttpResponseRedirect(success_url)

    if _rate_limited(request):
        if wants_json:
            return JsonResponse({"ok": False, "message": strings["form_rate"], "errors": {}}, status=429)
        form.add_error(None, strings["form_rate"])
        context = _build_context(request, lang, form=form)
        return render(request, "portfolio/index.html", context, status=429)

    if not form.is_valid():
        if wants_json:
            errors = {field: errs[0] for field, errs in form.errors.items() if field != "__all__"}
            return JsonResponse({"ok": False, "message": strings["form_error"], "errors": errors}, status=400)
        context = _build_context(request, lang, form=form)
        return render(request, "portfolio/index.html", context, status=400)

    msg = ContactMessage.objects.create(
        name=form.cleaned_data["name"],
        contact=form.cleaned_data["contact"],
        message=form.cleaned_data["message"],
        lang=lang,
    )
    if notify_new_message(msg):
        ContactMessage.objects.filter(pk=msg.pk).update(telegram_sent=True)

    if wants_json:
        return JsonResponse({"ok": True, "message": strings["form_success"]})
    return HttpResponseRedirect(success_url)


# ---------------------------------------------------------------------------
# SEO plumbing
# ---------------------------------------------------------------------------

@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


@require_GET
def sitemap_xml(request):
    urls = {code: request.build_absolute_uri(f"/{code}/") for code in SUPPORTED_LANGUAGES}
    alternates = "".join(
        f'    <xhtml:link rel="alternate" hreflang="{code}" href="{url}"/>\n' for code, url in urls.items()
    ) + f'    <xhtml:link rel="alternate" hreflang="x-default" href="{request.build_absolute_uri("/")}"/>\n'
    entries = "".join(
        f"  <url>\n    <loc>{url}</loc>\n{alternates}    <changefreq>weekly</changefreq>\n  </url>\n"
        for url in urls.values()
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        f"{entries}</urlset>\n"
    )
    return HttpResponse(xml, content_type="application/xml")
