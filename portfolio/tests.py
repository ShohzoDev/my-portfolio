import json
import re

from django.test import TestCase, override_settings
from django.urls import reverse

from .content import STACK, STRINGS, SUPPORTED_LANGUAGES
from .models import LoginFailure, Project, SiteProfile, SocialLink
from .views import _asset_version

# The index template uses {% static %}, and production uses WhiteNoise's
# manifest storage (hashed filenames, requires `collectstatic`). Django's test
# runner forces DEBUG=False, which makes that storage strict about missing
# manifest entries — so tests that render the real template use the plain
# storage instead. Unrelated to what these tests verify.
_TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


class SocialLinkModelTests(TestCase):
    def test_has_link(self):
        self.assertFalse(SocialLink(platform="instagram", url="").has_link)
        self.assertTrue(SocialLink(platform="github", url="https://github.com/x").has_link)

    def test_display_name(self):
        self.assertEqual(SocialLink(platform="telegram").display_name, "Telegram")
        self.assertEqual(SocialLink(platform="other", label="Behance").display_name, "Behance")

    def test_ordering_is_respected(self):
        SocialLink.objects.all().delete()  # 0002 migration seeds defaults
        SocialLink.objects.create(platform="x", order=2)
        SocialLink.objects.create(platform="github", order=0)
        SocialLink.objects.create(platform="telegram", order=1)
        self.assertEqual(
            list(SocialLink.objects.values_list("platform", flat=True)), ["github", "telegram", "x"]
        )


class ProjectModelTests(TestCase):
    def test_content_migration_sets_up_link_list(self):
        listed = list(Project.objects.filter(is_active=True).values_list("slug", "link"))
        self.assertEqual(
            listed,
            [
                ("zebest", "https://zebest.uz"),
                ("buildbest", "https://buildbest.uz"),
                ("oqqushlar", "https://oqqushlar.uz"),
                ("geodezistman", "https://geodezistman.uz"),
                ("roma-food", "https://romafood.pythonanywhere.com"),
            ],
        )
        self.assertFalse(Project.objects.filter(slug__in=("buildops", "eltaom")).exists())  # renamed
        for slug in ("lingvoapp", "english-bot", "n8n-workflows", "geo-portfolio"):
            self.assertFalse(Project.objects.get(slug=slug).is_active, slug)
        self.assertTrue(Project.objects.get(slug="zebest").is_founder)
        self.assertEqual(SiteProfile.objects.count(), 1)

    def test_every_project_is_translated_in_one_line(self):
        for p in Project.objects.filter(is_active=True):
            for lang in SUPPORTED_LANGUAGES:
                with self.subTest(project=p.slug, lang=lang):
                    self.assertTrue(getattr(p, f"title_{lang}"))
                    desc = getattr(p, f"desc_{lang}")
                    self.assertTrue(desc)
                    self.assertLessEqual(len(desc), 90)  # one line, not a paragraph
                    self.assertNotIn("\n", desc)

    def test_domain_is_what_the_visitor_reads(self):
        cases = {
            "https://zebest.uz": "zebest.uz",
            "https://www.Oqqushlar.uz/": "oqqushlar.uz",
            "http://app.buildbest.uz:8000/login/?next=/": "app.buildbest.uz",
            "": "",
        }
        for link, domain in cases.items():
            self.assertEqual(Project(link=link).domain, domain, link)

    def test_localized(self):
        data = Project.objects.get(slug="buildbest").localized("ru")
        self.assertEqual(data["title"], "BuildBest")
        self.assertEqual(data["domain"], "buildbest.uz")
        self.assertIn("строительных", data["desc"])
        self.assertEqual(set(data), {"slug", "title", "desc", "status", "is_founder", "link", "domain"})


class ContentTests(TestCase):
    def test_all_languages_have_identical_keys(self):
        keys = set(STRINGS["uz"])
        for lang in SUPPORTED_LANGUAGES:
            self.assertEqual(set(STRINGS[lang]), keys, lang)

    def test_every_label_is_filled(self):
        for lang in SUPPORTED_LANGUAGES:
            for key, value in STRINGS[lang].items():
                self.assertTrue(value.strip(), f"{lang}.{key}")


@override_settings(STORAGES=_TEST_STORAGES)
class LanguageRoutingTests(TestCase):
    def test_root_defaults_to_uzbek(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/uz/", fetch_redirect_response=False)

    def test_root_follows_accept_language(self):
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="de-DE,ru;q=0.8,en;q=0.5")
        self.assertRedirects(response, "/ru/", fetch_redirect_response=False)

    def test_accept_language_respects_q_values(self):
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="ru;q=0.3, en;q=0.9")
        self.assertRedirects(response, "/en/", fetch_redirect_response=False)

    def test_cookie_beats_accept_language(self):
        self.client.cookies["site_lang"] = "en"
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="ru")
        self.assertRedirects(response, "/en/", fetch_redirect_response=False)

    def test_root_varies_on_cookie_and_language(self):
        vary = self.client.get("/")["Vary"]
        self.assertIn("Cookie", vary)
        self.assertIn("Accept-Language", vary)

    def test_unknown_language_is_404(self):
        self.assertEqual(self.client.get("/fr/").status_code, 404)

    def test_each_language_renders_in_its_own_language(self):
        for lang in SUPPORTED_LANGUAGES:
            with self.subTest(lang=lang):
                response = self.client.get(f"/{lang}/")
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, f'<html lang="{lang}">')
                self.assertContains(response, STRINGS[lang]["hero_role"])

    def test_visiting_a_language_remembers_it(self):
        response = self.client.get("/ru/")
        self.assertEqual(response.cookies["site_lang"].value, "ru")


@override_settings(STORAGES=_TEST_STORAGES)
class IndexPageTests(TestCase):
    def get(self, lang="uz"):
        return self.client.get(f"/{lang}/").content.decode()

    def test_hreflang_alternates_and_canonical(self):
        html = self.get("en")
        for lang in SUPPORTED_LANGUAGES:
            self.assertIn(f'hreflang="{lang}" href="http://testserver/{lang}/"', html)
        self.assertIn('hreflang="x-default" href="http://testserver/"', html)
        self.assertIn('<link rel="canonical" href="http://testserver/en/">', html)

    def test_json_ld_person_is_valid(self):
        html = self.get("en")
        match = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(data["@type"], "Person")
        self.assertEqual(data["jobTitle"], STRINGS["en"]["hero_role"])
        self.assertEqual(data["knowsAbout"], STACK)
        self.assertIn("https://github.com/ShohzoDev", data["sameAs"])
        self.assertIn("https://t.me/ShohzoDev", data["sameAs"])

    def test_header_hero_and_sections(self):
        for lang in SUPPORTED_LANGUAGES:
            strings = STRINGS[lang]
            html = self.get(lang)
            self.assertIn('<header class="site-header">', html)
            self.assertEqual(re.findall(r'<section class="[a-z ]+" id="([a-z]+)"', html),
                             ["top", "about", "services", "projects", "contact"])
            # header menu (desktop) and mobile menu both point at every section, in page order
            nav = html[html.index('<nav class="nav"'):html.index('</nav>', html.index('<nav class="nav"'))]
            self.assertEqual(re.findall(r'href="#([a-z]+)"', nav), ["about", "services", "projects", "contact"])
            self.assertIn('<details class="menu">', html)
            self.assertIn(strings["hero_hello"].replace("'", "&#x27;") + " <em>Shohzod</em>.", html)
            self.assertIn(f"// {strings['hero_role']}", html)
            self.assertIn(strings["header_cta"].replace("'", "&#x27;"), html)
            for n in range(1, 5):
                self.assertIn(strings[f"s{n}_t"].replace("'", "&#x27;"), html)
            self.assertNotIn("*", html[html.index('<div class="about">'):html.index('<ul class="chips">')])
            self.assertIn('<a href="https://zebest.uz" target="_blank" rel="noopener">Zebest</a>', html)
            hero = html[html.index('<section class="hero"'):html.index('id="about"')]
            self.assertIn('class="portrait"', hero)  # the face is in the first screen
            self.assertIn(strings["fact_langs_value"].replace("'", "&#x27;"), html)
            for tool in STACK:
                self.assertIn(f"<li>{tool}</li>", html)
            self.assertNotIn("{#", html)  # no leaked template syntax
            self.assertNotIn("{%", html)
            for gone in ('class="diagram', "<form", "cmdk", "script.js", "menu.js", 'class="side"'):
                self.assertNotIn(gone, html)

    def test_code_window_is_valid_python(self):
        """The hero code is real, runnable Python — in every language."""
        import ast
        import html as html_lib

        for lang in SUPPORTED_LANGUAGES:
            page = self.get(lang)
            block = page[page.index('<pre class="code" id="code"><code>'):page.index("</code></pre>")]
            lines = re.findall(r'<span class="ln(?: ln-extra)?">(.*?)</span>(?=<span class="ln|$)', block, re.S)
            self.assertEqual(len(lines), 9)
            text = "\n".join(html_lib.unescape(re.sub(r"<[^>]+>", "", ln)) for ln in lines)
            self.assertIn('name     = "Shohzod"', text)
            self.assertIn(STRINGS[lang]["code_status"], text)
            self.assertIn("return idea.to_production()", text)
            ast.parse(text)  # raises SyntaxError if the snippet is broken

    def test_assets_carry_a_cache_busting_version(self):
        html = self.get("en")
        version = _asset_version()
        self.assertGreater(version, 0)
        self.assertIn(f'/static/portfolio/css/style.css?v={version}"', html)
        self.assertIn(f'/static/portfolio/js/site.js?v={version}"', html)

    def test_highlight_filter(self):
        from .templatetags.portfolio_extras import highlight

        projects = [{"title": "Zebest", "link": "https://zebest.uz"}, {"title": "Draft", "link": ""}]
        out = highlight("I *founded* Zebest, not Draft. Zebest again <script>", projects)
        self.assertEqual(
            out,
            'I <strong>founded</strong> <a href="https://zebest.uz" target="_blank" rel="noopener">Zebest</a>,'
            " not Draft. Zebest again &lt;script&gt;",  # first mention only; text is escaped
        )

    def test_projects_are_rows_linking_to_their_sites(self):
        html = self.get("en")
        section = html[html.index('id="projects"'):html.index('id="contact"')]
        rows = re.findall(r'<li id="p-([a-z-]+)">\s*<a class="row is-link" href="([^"]+)" target="_blank" rel="noopener">', section)
        self.assertEqual(
            rows,
            [
                ("zebest", "https://zebest.uz"),
                ("buildbest", "https://buildbest.uz"),
                ("oqqushlar", "https://oqqushlar.uz"),
                ("geodezistman", "https://geodezistman.uz"),
                ("roma-food", "https://romafood.pythonanywhere.com"),
            ],
        )
        for domain in ("zebest.uz", "buildbest.uz", "oqqushlar.uz", "geodezistman.uz"):
            self.assertIn(f'<span class="row-side">{domain}</span>', section)
        self.assertNotIn("https://", re.sub(r'href="[^"]+"', "", section))  # domains shown bare
        self.assertNotIn("BuildOps", html)
        self.assertNotIn("p-geo-portfolio", html)
        self.assertNotIn("p-lingvoapp", html)

    def test_project_without_site_is_not_a_link(self):
        Project.objects.filter(slug="lingvoapp").update(is_active=True)
        html = self.get("en")
        row = html[html.index('id="p-lingvoapp"'):]
        row = row[:row.index("</li>")]
        self.assertIn('<div class="row">', row)
        self.assertIn(STRINGS["en"]["status_dev"], row)  # non-live status is spelled out
        self.assertNotIn("href=", row)

    def test_inactive_project_is_hidden(self):
        Project.objects.filter(slug="roma-food").update(is_active=False)
        self.assertNotIn('id="p-roma-food"', self.get())

    def test_zebest_founder_badge(self):
        for lang in SUPPORTED_LANGUAGES:
            html = self.get(lang)
            row = html[html.index('id="p-zebest"'):]
            self.assertIn(STRINGS[lang]["founder_label"], row[:row.index("</li>")])
        row = html[html.index('id="p-buildbest"'):]
        self.assertNotIn("founder-tag", row[:row.index("</li>")])

    def test_only_linked_social_icons_are_shown(self):
        html = self.get()
        for url in ("https://github.com/ShohzoDev", "https://t.me/ShohzoDev",
                    "https://www.instagram.com/ShohzoDev/", "https://x.com/ShohzoDev",
                    "https://www.facebook.com/ShohzoDev"):
            self.assertIn(f'href="{url}"', html)
        self.assertNotIn("ShohzoDev0108", html)
        self.assertIn('<meta name="twitter:creator" content="@ShohzoDev">', html)
        SocialLink.objects.create(platform="linkedin", url="")  # no URL yet
        self.assertNotIn('title="LinkedIn"', self.get())
        SocialLink.objects.filter(platform="linkedin").update(url="https://linkedin.com/in/someone")
        self.assertIn('title="LinkedIn"', self.get())

    def test_telegram_is_the_main_button(self):
        html = self.get("en")
        self.assertIn('href="https://t.me/ShohzoDev" target="_blank" rel="noopener">'
                      + STRINGS["en"]["contact_telegram_btn"], html)
        self.assertIn('href="https://t.me/ShohzoDev" target="_blank" rel="noopener">'
                      + STRINGS["en"]["header_cta"].replace("'", "&#x27;"), html)
        SocialLink.objects.filter(platform="telegram").update(url="")
        self.assertNotIn(STRINGS["en"]["contact_telegram_btn"], self.get("en"))

    @override_settings(SITE_CONTACT_EMAIL="contact@example.com")
    def test_placeholder_email_is_never_shown(self):
        html = self.get("en")
        self.assertNotIn("example.com", html)
        self.assertNotIn("mailto:", html)

    @override_settings(SITE_CONTACT_EMAIL="hello@real.uz")
    def test_real_email_is_shown(self):
        self.assertIn('<a class="email" href="mailto:hello@real.uz">hello@real.uz</a>', self.get("en"))

    def test_profile_name_comes_from_admin(self):
        SiteProfile.objects.update(full_name="Shohzod Testov")
        html = self.get("en")
        self.assertIn("<title>Shohzod Testov — Django Backend Engineer</title>", html)
        self.assertIn('<em>Shohzod Testov</em>', html)
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(data["name"], "Shohzod Testov")

    def test_in_page_links_have_targets(self):
        html = self.get("en")
        for href in re.findall(r'href="#([a-z-]+)"', html):
            self.assertIn(f'id="{href}"', html, href)

    def test_robots_and_sitemap(self):
        robots = self.client.get(reverse("portfolio:robots_txt")).content.decode()
        self.assertNotIn("admin", robots)  # don't advertise the admin path
        self.assertIn("Sitemap: http://testserver/sitemap.xml", robots)
        sitemap = self.client.get(reverse("portfolio:sitemap_xml")).content.decode()
        for lang in SUPPORTED_LANGUAGES:
            self.assertIn(f"<loc>http://testserver/{lang}/</loc>", sitemap)
        self.assertIn('hreflang="x-default"', sitemap)
        self.assertEqual(sitemap.count("<loc>"), 3)


@override_settings(STORAGES=_TEST_STORAGES)
class ErrorPageTests(TestCase):
    def test_removed_pages_are_gone(self):
        self.assertEqual(self.client.get("/uz/work/zebest/").status_code, 404)  # old case studies
        self.assertEqual(self.client.post("/uz/contact/").status_code, 404)  # old contact form

    @override_settings(DEBUG=False)
    def test_error_pages_have_no_inline_styles(self):
        response = self.client.get("/uz/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        html = response.content.decode()
        self.assertNotIn("<style", html)
        self.assertIn('href="/static/portfolio/css/error.css"', html)
        self.assertIn("Content-Security-Policy", response)


@override_settings(STORAGES=_TEST_STORAGES)
class SecurityTests(TestCase):
    def test_csp_header_and_no_executable_scripts(self):
        from .security import CONTENT_SECURITY_POLICY

        response = self.client.get("/en/")
        csp = response["Content-Security-Policy"]
        self.assertEqual(csp, CONTENT_SECURITY_POLICY)
        self.assertIn("script-src 'self'", csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn("camera=()", response["Permissions-Policy"])
        html = response.content.decode()
        # JSON-LD data (never executes) and the one external script — no inline code.
        self.assertEqual(
            re.findall(r"<script([^>]*)>", html),
            [' type="application/ld+json"', f' src="/static/portfolio/js/site.js?v={_asset_version()}" defer'],
        )
        self.assertNotIn(" style=", html)  # style-src 'self' forbids inline styles

    def test_admin_is_left_without_csp(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Content-Security-Policy", response)

    def test_admin_login_is_throttled_after_repeated_failures(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_superuser("boss", "boss@x.uz", "correct-horse-battery")
        url = "/admin/login/?next=/admin/"
        with self.assertLogs("portfolio.security", level="WARNING"):
            for _ in range(5):
                response = self.client.post(url, {"username": "boss", "password": "wrong"})
                self.assertEqual(response.status_code, 200)  # normal "wrong password" page
            self.assertEqual(LoginFailure.objects.count(), 5)
            blocked = self.client.post(url, {"username": "boss", "password": "correct-horse-battery"})
        self.assertEqual(blocked.status_code, 429)

    def test_successful_login_works_below_the_limit(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_superuser("boss", "boss@x.uz", "correct-horse-battery")
        with self.assertLogs("portfolio.security", level="WARNING"):
            self.client.post("/admin/login/", {"username": "boss", "password": "wrong"})
        ok = self.client.post("/admin/login/?next=/admin/", {"username": "boss", "password": "correct-horse-battery"})
        self.assertRedirects(ok, "/admin/", fetch_redirect_response=False)

    @override_settings(ADMIN_LOGIN_GLOBAL_MAX_FAILURES=3)
    def test_admin_login_global_cap(self):
        for i in range(3):
            LoginFailure.objects.create(ip_hash=f"other-{i}")
        response = self.client.post("/admin/login/", {"username": "x", "password": "y"})
        self.assertEqual(response.status_code, 429)

    @override_settings(DEBUG=False, SITE_CONTACT_EMAIL="contact@example.com")
    def test_system_check_warns_about_placeholder_email(self):
        from .apps import contact_email_configured

        self.assertEqual([w.id for w in contact_email_configured(None)], ["portfolio.W001"])


class UzbekAlphabetTests(TestCase):
    def test_converter(self):
        from .uz_alphabet import to_new_latin as t

        self.assertEqual(t("Bog'lanish uchun to'g'ridan-to'g'ri yozing"), "Boğlaniş uçun töğridan-töğri yozing")
        self.assertEqual(t("Shunga o'xshash tizim kerakmi?"), "Şunga öxşaş tizim kerakmi?")
        self.assertEqual(t("ta'lim va ma'lumot, tong"), "ta'lim va ma'lumot, tong")  # tutuq, ng stay
        self.assertEqual(t("AI-yordamchi"), "AI-yordamçi")
        for name in ("Oqqushlar", "oqqushlar.uz", "ShohzoDev", "Shohzod", "schema-per-tenant",
                     "Health-check", "English", "Django'da"):
            self.assertEqual(t(name), name)
        once = t("O'zbekiston, Toshkent, qirg'iz")
        self.assertEqual(once, "Özbekiston, Toşkent, qirğiz")
        self.assertEqual(t(once), once)  # idempotent

    @override_settings(STORAGES=_TEST_STORAGES)
    def test_uzbek_pages_use_the_new_alphabet(self):
        import html as html_lib

        from .uz_alphabet import to_new_latin

        for path in ("/uz/",):
            page = self.client.get(path).content.decode()
            text = html_lib.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", page, flags=re.S))
            for word in re.findall(r"[^\s«»\"()\[\],;:!?—–/|·]+", text):
                # Anything the converter would still change is a leftover old spelling;
                # names and technical words are protected by the converter itself.
                self.assertEqual(to_new_latin(word), word, f"{path}: old spelling {word!r}")
            self.assertIn("Özbekça", page)

    @override_settings(STORAGES=_TEST_STORAGES)
    def test_russian_and_english_are_untouched(self):
        self.assertIn(STRINGS["en"]["contact_title"], self.client.get("/en/").content.decode())
        self.assertNotIn("ş", STRINGS["en"]["hero_tagline"] + STRINGS["ru"]["hero_tagline"])

class BlankEnvSettingsTests(TestCase):
    """Regression: `KEY=` lines in .env (as in .env.example) are empty strings,
    not missing variables. They must fall back to defaults — an empty
    SECRET_KEY once crashed every request with a bare "A server error occurred"."""

    def test_blank_env_values_fall_back_to_defaults(self):
        import os
        import subprocess
        import sys

        from django.conf import settings as dj_settings

        blank = {
            "DJANGO_SECRET_KEY": "",
            "DJANGO_DEBUG": "",
            "DJANGO_ALLOWED_HOSTS": "",
            "SITE_CONTACT_EMAIL": "",
            "ADMIN_LOGIN_MAX_FAILURES": "",
        }
        code = (
            "import json, django; django.setup();"
            "from django.conf import settings as s;"
            "print(json.dumps([s.SECRET_KEY, s.DEBUG, s.ALLOWED_HOSTS,"
            " s.SITE_CONTACT_EMAIL, s.ADMIN_LOGIN_MAX_FAILURES]))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=dj_settings.BASE_DIR,
            env={**os.environ, **blank, "DJANGO_SETTINGS_MODULE": "config.settings"},
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        secret, debug, hosts, email, rate = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertTrue(secret)
        self.assertTrue(debug)
        self.assertEqual(hosts, ["127.0.0.1", "localhost"])
        self.assertEqual(email, "contact@example.com")
        self.assertEqual(rate, 5)
