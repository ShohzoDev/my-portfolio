import json
from datetime import timedelta

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
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
from .models import ContactMessage, Project, SiteProfile, SocialLink
from .notifications import notify_new_message
from .security import client_ip, ip_hash

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


def _public_email():
    """The contact address, or "" while it is still the placeholder."""
    email = settings.SITE_CONTACT_EMAIL
    return "" if email.endswith("@example.com") else email


def _localized_projects(lang):
    strings = STRINGS[lang]
    projects = [p.localized(lang) for p in Project.objects.filter(is_active=True)]
    for p in projects:
        p["status_label"] = strings[f"status_{p['status']}"]
    return projects


def _commands(strings, lang, projects, email, github_url, alternates, on_home):
    """⌘K palette entries, already translated — the JS just filters/executes.

    On the home page sections scroll in place; on a case page the same
    entries navigate back to the home page section.
    """
    home = f"/{lang}/"

    def goto(target, label, group):
        if on_home:
            return {"group": group, "label": label, "kind": "scroll", "target": target}
        return {"group": group, "label": label, "kind": "href", "href": home + target}

    commands = [
        goto(target, strings[key], strings["cmdk_group_nav"])
        for key, target in (
            ("nav_top", "#top"),
            ("nav_projects", "#projects"),
            ("nav_about", "#about"),
            ("nav_contact", "#contact"),
        )
    ]
    for p in projects:
        if p["has_case"]:
            commands.append(
                {"group": strings["cmdk_group_projects"], "label": p["title"], "kind": "href",
                 "href": reverse("portfolio:case", args=[lang, p["slug"]])}
            )
        elif p["link"]:
            commands.append(
                {"group": strings["cmdk_group_projects"], "label": p["title"], "kind": "href",
                 "href": p["link"], "external": True}
            )
    if email:
        commands += [
            {"group": strings["cmdk_group_actions"], "label": strings["cmdk_copy_email"], "kind": "copy", "value": email,
             "done": strings["contact_email_copied"]},
            {"group": strings["cmdk_group_actions"], "label": strings["contact_email_btn"], "kind": "href", "href": f"mailto:{email}"},
        ]
    commands.append(
        {"group": strings["cmdk_group_actions"], "label": strings["cmdk_github"], "kind": "href", "href": github_url, "external": True}
    )
    commands += [
        {"group": strings["cmdk_group_lang"], "label": alt["name"], "kind": "href", "href": alt["path"], "current": alt["code"] == lang}
        for alt in alternates
    ]
    return commands


def _base_context(request, lang, path_for, *, on_home, projects):
    """Everything base.html needs. `path_for(code)` builds this page's URL in
    another language (used for hreflang, canonical and the language switch)."""
    strings = STRINGS[lang]
    profile = SiteProfile.load()
    social_links = [s for s in SocialLink.objects.filter(is_active=True) if s.has_link]
    telegram_url = next((s.url for s in social_links if s.platform == SocialLink.Platform.TELEGRAM), "")
    github_url = f"https://github.com/{settings.SITE_GITHUB_USERNAME}"
    email = _public_email()

    alternates = [
        {"code": code, "name": LANGUAGE_NAMES[code], "path": path_for(code),
         "url": request.build_absolute_uri(path_for(code))}
        for code in SUPPORTED_LANGUAGES
    ]
    return {
        "lang": lang,
        "strings": strings,
        "profile": profile,
        "social_links": social_links,
        "telegram_url": telegram_url,
        "contact_email": email,
        "github_url": github_url,
        "home_url": "" if on_home else f"/{lang}/",
        "canonical_url": request.build_absolute_uri(path_for(lang)),
        "alternates": alternates,
        "x_default_url": request.build_absolute_uri("/"),
        "og_image_url": _abs_static(request, "portfolio/img/og-image.jpg"),
        "og_locale": OG_LOCALES[lang],
        "og_locale_alternates": [OG_LOCALES[c] for c in SUPPORTED_LANGUAGES if c != lang],
        "commands": _commands(strings, lang, projects, email, github_url, alternates, on_home),
    }


def _person(request, lang, profile, strings, social_links, github_url, email, skills):
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
        "knowsAbout": sorted({tag for group in skills for tag in group["tags"]}),
        "sameAs": [github_url] + [s.url for s in social_links if s.url != github_url],
    }
    if email:
        person["email"] = f"mailto:{email}"
    return person


def _home_context(request, lang, form=None, sent=False):
    projects = _localized_projects(lang)
    context = _base_context(request, lang, lambda code: f"/{code}/", on_home=True, projects=projects)
    strings = context["strings"]
    skills = localized_skills(lang)
    live_count = sum(1 for p in projects if p["status"] == Project.Status.LIVE)
    person = _person(request, lang, context["profile"], strings, context["social_links"],
                     context["github_url"], context["contact_email"], skills)
    context.update(
        {
            "featured_projects": [p for p in projects if p["tier"] == Project.Tier.FEATURED],
            "other_projects": [p for p in projects if p["tier"] != Project.Tier.FEATURED],
            "skills": skills,
            "about_paragraphs": context["profile"].about_paragraphs(lang),
            "how_items": [
                {"n": f"0{i}", "title": strings[f"how{i}_t"], "text": strings[f"how{i}_d"]} for i in range(1, 5)
            ],
            "live_count": live_count,
            "badge_label": strings[plural_key(lang, live_count)],
            "page_title": f"{context['profile'].full_name} — {strings['hero_role']}",
            "page_description": strings["hero_tagline"],
            "jsonld": _json_for_script(person),
            "form": form or ContactForm(lang=lang),
            "sent": sent,
        }
    )
    return context


def _remember_language(response, lang):
    response.set_cookie(LANG_COOKIE, lang, max_age=LANG_COOKIE_MAX_AGE, samesite="Lax")
    return response


@require_GET
def index(request, lang):
    context = _home_context(request, lang, sent=request.GET.get("sent") == "1")
    return _remember_language(render(request, "portfolio/index.html", context), lang)


@require_GET
def case_detail(request, lang, slug):
    projects = _localized_projects(lang)
    project = next((p for p in projects if p["slug"] == slug and p["has_case"]), None)
    if project is None:
        raise Http404("No case study for this project")

    context = _base_context(
        request, lang, lambda code: reverse("portfolio:case", args=[code, slug]), on_home=False, projects=projects
    )
    strings = context["strings"]
    cases = [p for p in projects if p["has_case"]]
    next_project = cases[(cases.index(project) + 1) % len(cases)] if len(cases) > 1 else None
    work = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": project["title"],
        "description": project["desc"],
        "url": context["canonical_url"],
        "inLanguage": lang,
        "keywords": ", ".join(project["tags"]),
        "author": {"@type": "Person", "name": context["profile"].full_name, "url": request.build_absolute_uri(f"/{lang}/")},
    }
    if project["link"]:
        work["sameAs"] = project["link"]
    context.update(
        {
            "project": project,
            "next_project": next_project,
            "page_title": f"{project['title']} — {context['profile'].full_name}",
            "page_description": project["desc"],
            "jsonld": _json_for_script(work),
        }
    )
    return _remember_language(render(request, "portfolio/case.html", context), lang)


# ---------------------------------------------------------------------------
# Contact form
# ---------------------------------------------------------------------------

def _rate_limited(hashed_ip):
    """Counted in the database, so the limit holds across every gunicorn
    worker and survives restarts (an in-memory cache would give each worker
    its own counter)."""
    since = timezone.now() - timedelta(hours=1)
    recent = ContactMessage.objects.filter(created_at__gte=since)
    if recent.filter(ip_hash=hashed_ip).count() >= settings.CONTACT_RATE_LIMIT_PER_HOUR:
        return True
    return recent.count() >= settings.CONTACT_GLOBAL_LIMIT_PER_HOUR


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

    hashed_ip = ip_hash(client_ip(request))
    if _rate_limited(hashed_ip):
        if wants_json:
            return JsonResponse({"ok": False, "message": strings["form_rate"], "errors": {}}, status=429)
        form.add_error(None, strings["form_rate"])
        return render(request, "portfolio/index.html", _home_context(request, lang, form=form), status=429)

    if not form.is_valid():
        if wants_json:
            errors = {field: errs[0] for field, errs in form.errors.items() if field != "__all__"}
            return JsonResponse({"ok": False, "message": strings["form_error"], "errors": errors}, status=400)
        return render(request, "portfolio/index.html", _home_context(request, lang, form=form), status=400)

    msg = ContactMessage.objects.create(
        name=form.cleaned_data["name"],
        contact=form.cleaned_data["contact"],
        message=form.cleaned_data["message"],
        lang=lang,
        ip_hash=hashed_ip,
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
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


@require_GET
def sitemap_xml(request):
    """Home page + every case-study page, each in 3 languages with hreflang."""
    pages = [(lambda code: f"/{code}/", True)]
    for slug in [p.slug for p in Project.objects.filter(is_active=True) if p.has_case]:
        pages.append((lambda code, slug=slug: reverse("portfolio:case", args=[code, slug]), False))

    entries = ""
    for path_for, is_home in pages:
        urls = {code: request.build_absolute_uri(path_for(code)) for code in SUPPORTED_LANGUAGES}
        alternates = "".join(
            f'    <xhtml:link rel="alternate" hreflang="{code}" href="{url}"/>\n' for code, url in urls.items()
        )
        if is_home:
            alternates += f'    <xhtml:link rel="alternate" hreflang="x-default" href="{request.build_absolute_uri("/")}"/>\n'
        entries += "".join(
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
