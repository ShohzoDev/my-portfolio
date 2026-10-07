import json
import re
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from .content import STRINGS, SUPPORTED_LANGUAGES, localized_skills, plural_key
from .models import ContactMessage, LoginFailure, Project, SiteProfile, SocialLink

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
    def test_content_migration_sets_up_compact_lineup(self):
        featured = list(
            Project.objects.filter(is_active=True, tier=Project.Tier.FEATURED).values_list("slug", flat=True)
        )
        self.assertEqual(featured, ["buildops", "oqqushlar", "zebest"])
        for slug in featured:
            self.assertTrue(Project.objects.get(slug=slug).has_case, slug)
        self.assertFalse(Project.objects.filter(slug="eltaom").exists())  # renamed to Zebest
        self.assertFalse(Project.objects.get(slug="geo-portfolio").is_active)
        self.assertEqual(Project.objects.get(slug="buildops").link, "")  # client site not published
        self.assertEqual(SiteProfile.objects.count(), 1)

    def test_every_project_is_translated(self):
        for p in Project.objects.all():
            for lang in SUPPORTED_LANGUAGES:
                with self.subTest(project=p.slug, lang=lang):
                    self.assertTrue(getattr(p, f"title_{lang}"))
                    self.assertTrue(getattr(p, f"desc_{lang}"))

    def test_localized_and_tag_list(self):
        p = Project.objects.get(slug="buildops")
        data = p.localized("en")
        self.assertEqual(data["title"], p.title_en)
        self.assertIn("Django", data["tags"])
        self.assertEqual(len(data["highlights"]), 6)
        self.assertEqual(len(data["facts"]), 3)
        self.assertEqual(len(data["solution"]), 3)  # blank-line separated paragraphs
        self.assertEqual(data["cover"], "")

    def test_every_case_is_fully_translated(self):
        for p in Project.objects.filter(is_active=True):
            if not p.has_case:
                continue
            for lang in SUPPORTED_LANGUAGES:
                for field in ("facts", "problem", "solution", "result", "highlights"):
                    with self.subTest(project=p.slug, lang=lang, field=field):
                        self.assertTrue(getattr(p, f"{field}_{lang}").strip())


class ContentTests(TestCase):
    def test_all_languages_have_identical_keys(self):
        keys = set(STRINGS["uz"])
        for lang in SUPPORTED_LANGUAGES:
            self.assertEqual(set(STRINGS[lang]), keys, lang)

    def test_localized_skills(self):
        self.assertIn("Backend", [s["title"] for s in localized_skills("ru")])

    def test_russian_plural(self):
        self.assertEqual(plural_key("ru", 1), "badge_label_one")
        self.assertEqual(plural_key("ru", 4), "badge_label_few")
        self.assertEqual(plural_key("ru", 5), "badge_label_many")
        self.assertEqual(plural_key("ru", 11), "badge_label_many")
        self.assertEqual(plural_key("ru", 22), "badge_label_few")
        self.assertEqual(plural_key("en", 1), "badge_label_one")
        self.assertEqual(plural_key("en", 4), "badge_label_many")


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
        self.assertIn("https://github.com/ShohzoDev", data["sameAs"])
        self.assertIn("https://t.me/ShohzoDev", data["sameAs"])

    def test_content_is_server_rendered(self):
        html = self.get()
        self.assertIn("BuildOps", html)
        self.assertIn("Django backend muhandisiman", html)  # About text from SiteProfile

    def test_project_tiers_render_in_their_sections(self):
        html = self.get("en")
        work = html[html.index('class="work-grid"'):html.index('class="other-list"')]
        for slug in ("buildops", "oqqushlar", "zebest"):
            self.assertIn(f'id="p-{slug}"', work)
            self.assertIn(f'href="/en/work/{slug}/"', work)
        other = html[html.index('class="other-list"'):]
        for slug in ("roma-food", "geodezistman", "lingvoapp", "english-bot", "n8n-workflows"):
            self.assertIn(f'id="p-{slug}"', other)
        self.assertNotIn("p-geo-portfolio", html)
        self.assertNotIn("Eltaom", html)

    def test_badge_counts_only_live_projects(self):
        live = Project.objects.filter(is_active=True, status=Project.Status.LIVE).count()
        html = self.get("ru")
        self.assertIn(f"{live} — {STRINGS['ru'][plural_key('ru', live)]}", html)
        self.assertEqual(live, 4)
        self.assertIn(STRINGS["ru"][plural_key("ru", live)], html)

    def test_inactive_project_is_hidden(self):
        Project.objects.filter(slug="lingvoapp").update(is_active=False)
        self.assertNotIn('id="p-lingvoapp"', self.get())

    def test_only_linked_social_icons_are_shown(self):
        html = self.get()
        for url in ("https://github.com/ShohzoDev", "https://t.me/ShohzoDev",
                    "https://www.instagram.com/ShohzoDev/", "https://x.com/ShohzoDev"):
            self.assertIn(f'href="{url}"', html)
        self.assertNotIn("ShohzoDev0108", html)
        self.assertNotIn('title="Facebook"', html)  # no URL yet
        SocialLink.objects.filter(platform="facebook").update(url="https://facebook.com/someone")
        self.assertIn('title="Facebook"', self.get())
        self.assertIn('<meta name="twitter:creator" content="@ShohzoDev">', html)

    def test_telegram_link_becomes_the_main_contact_button(self):
        SocialLink.objects.filter(platform="telegram").update(url="")
        self.assertNotIn(STRINGS["en"]["contact_telegram_btn"], self.get("en"))
        SocialLink.objects.filter(platform="telegram").update(url="https://t.me/someone")
        html = self.get("en")
        self.assertEqual(html.count('href="https://t.me/someone" class="btn'), 1)  # hero
        self.assertIn('class="btn btn-primary" href="https://t.me/someone"', html)  # contact

    @override_settings(SITE_CONTACT_EMAIL="contact@example.com")
    def test_placeholder_email_is_never_shown(self):
        html = self.get("en")
        self.assertNotIn("example.com", html)
        self.assertNotIn("mailto:", html)

    @override_settings(SITE_CONTACT_EMAIL="hello@real.uz")
    def test_real_email_is_shown(self):
        self.assertIn('href="mailto:hello@real.uz"', self.get("en"))

    def test_profile_name_and_about_come_from_admin(self):
        SiteProfile.objects.update(full_name="Shohzod Testov", about_en="First para.\n\nSecond para.")
        html = self.get("en")
        self.assertIn("<title>Shohzod Testov — Django Backend Engineer</title>", html)
        self.assertIn('<p class="lead">First para.</p><p>Second para.</p>', html)
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(data["name"], "Shohzod Testov")

    @override_settings(SITE_CONTACT_EMAIL="hello@real.uz")
    def test_command_palette_data(self):
        html = self.get("en")
        match = re.search(r'<script id="cmdk-commands" type="application/json">(.*?)</script>', html, re.S)
        commands = json.loads(match.group(1))
        kinds = {c["kind"] for c in commands}
        self.assertEqual(kinds, {"scroll", "href", "copy"})
        current = [c for c in commands if c.get("current")]
        self.assertEqual([c["href"] for c in current], ["/en/"])

    def test_redesign_sections_render(self):
        for lang in SUPPORTED_LANGUAGES:
            strings = STRINGS[lang]
            html = self.get(lang)
            self.assertIn('id="stack"', html)
            self.assertNotIn("{#", html)  # no leaked template comments
            self.assertNotIn("{%", html)
            self.assertIn('class="diagram"', html)
            self.assertIn('id="diagram-caption"', html)
            self.assertIn(f"<em>{strings['hero_headline_em']}</em>", html)
            for n in range(1, 5):
                self.assertIn(strings[f"how{n}_t"].replace("'", "&#x27;"), html)
            # every diagram node is keyboard-focusable and labelled, in both drawings
            self.assertEqual(html.count('class="node'), 18)
            self.assertEqual(html.count('tabindex="0"'), 18)

    def test_nav_targets_exist(self):
        html = self.get("en")
        match = re.search(r'<script id="cmdk-commands" type="application/json">(.*?)</script>', html, re.S)
        for c in json.loads(match.group(1)):
            if c["kind"] == "scroll":
                self.assertIn(f'id="{c["target"][1:]}"', html, c["target"])
        for href in re.findall(r'<a href="(#[a-z-]+)"', html):
            self.assertIn(f'id="{href[1:]}"', html, href)

    def test_robots_and_sitemap(self):
        robots = self.client.get(reverse("portfolio:robots_txt")).content.decode()
        self.assertNotIn("admin", robots)  # don't advertise the admin path
        self.assertIn("Sitemap: http://testserver/sitemap.xml", robots)
        sitemap = self.client.get(reverse("portfolio:sitemap_xml")).content.decode()
        for lang in SUPPORTED_LANGUAGES:
            self.assertIn(f"<loc>http://testserver/{lang}/</loc>", sitemap)
        self.assertIn('hreflang="x-default"', sitemap)
        for lang in SUPPORTED_LANGUAGES:
            self.assertIn(f"<loc>http://testserver/{lang}/work/buildops/</loc>", sitemap)
        self.assertNotIn("/work/roma-food/", sitemap)


@override_settings(STORAGES=_TEST_STORAGES, CONTACT_RATE_LIMIT_PER_HOUR=3)
class ContactFormTests(TestCase):
    valid = {"name": "Ali", "contact": "@ali", "message": "Salom, loyiha bor."}

    def post(self, data, lang="uz", ajax=False, **extra):
        headers = {"HTTP_X_REQUESTED_WITH": "fetch"} if ajax else {}
        return self.client.post(f"/{lang}/contact/", data, **headers, **extra)

    def test_valid_submission_saves_and_redirects(self):
        response = self.post(self.valid)
        self.assertRedirects(response, "/uz/?sent=1#contact", fetch_redirect_response=False)
        msg = ContactMessage.objects.get()
        self.assertEqual((msg.name, msg.lang, msg.telegram_sent), ("Ali", "uz", False))

    def test_success_message_shown_after_redirect(self):
        response = self.client.get("/uz/?sent=1")
        self.assertContains(response, STRINGS["uz"]["form_success"].replace("'", "&#x27;"))

    def test_ajax_valid(self):
        response = self.post(self.valid, lang="en", ajax=True)
        self.assertEqual(response.json(), {"ok": True, "message": STRINGS["en"]["form_success"]})

    def test_ajax_invalid_returns_translated_field_errors(self):
        response = self.post({"name": "", "contact": "", "message": ""}, lang="ru", ajax=True)
        self.assertEqual(response.status_code, 400)
        errors = response.json()["errors"]
        self.assertEqual(set(errors), {"name", "contact", "message"})
        self.assertEqual(errors["name"], STRINGS["ru"]["err_required"])
        self.assertFalse(ContactMessage.objects.exists())

    def test_invalid_without_js_rerenders_with_errors(self):
        response = self.post({"name": "Ali", "contact": "", "message": "hi"})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'aria-invalid="true"', status_code=400)
        self.assertContains(response, 'value="Ali"', status_code=400)  # input kept

    def test_honeypot_is_silently_dropped(self):
        response = self.post({**self.valid, "leave_empty": "http://spam.example"}, ajax=True)
        self.assertTrue(response.json()["ok"])
        self.assertFalse(ContactMessage.objects.exists())

    def test_rate_limit(self):
        for _ in range(3):
            self.assertEqual(self.post(self.valid, ajax=True).status_code, 200)
        blocked = self.post(self.valid, ajax=True)
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(ContactMessage.objects.count(), 3)

    def test_autofill_named_fields_are_not_honeypots(self):
        # Browsers autofill "website"/"url"; that must never drop a real message.
        response = self.post({**self.valid, "website": "https://my.site"}, ajax=True)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(ContactMessage.objects.count(), 1)

    @override_settings(CONTACT_TRUST_PROXY_HEADERS=True)
    def test_rate_limit_is_per_client_ip_behind_proxy(self):
        for _ in range(3):
            self.post(self.valid, ajax=True, HTTP_X_REAL_IP="1.1.1.1")
        self.assertEqual(self.post(self.valid, ajax=True, HTTP_X_REAL_IP="1.1.1.1").status_code, 429)
        other = self.post(self.valid, ajax=True, HTTP_X_REAL_IP="2.2.2.2")
        self.assertEqual(other.status_code, 200)

    @override_settings(CONTACT_TRUST_PROXY_HEADERS=True)
    def test_forwarded_for_uses_rightmost_entry(self):
        # The client controls the left part of X-Forwarded-For; only the
        # entry our own proxy appended (right-most) counts.
        for i in range(3):
            self.post(self.valid, ajax=True, HTTP_X_FORWARDED_FOR=f"9.9.9.{i}, 5.5.5.5")
        blocked = self.post(self.valid, ajax=True, HTTP_X_FORWARDED_FOR="8.8.8.8, 5.5.5.5")
        self.assertEqual(blocked.status_code, 429)

    def test_spoofed_proxy_headers_ignored_by_default(self):
        # Without a trusted proxy, rotating X-Real-IP must not bypass the limit.
        for i in range(3):
            self.post(self.valid, ajax=True, HTTP_X_REAL_IP=f"1.1.1.{i}")
        blocked = self.post(self.valid, ajax=True, HTTP_X_REAL_IP="7.7.7.7")
        self.assertEqual(blocked.status_code, 429)

    @override_settings(CONTACT_RATE_LIMIT_PER_HOUR=100, CONTACT_GLOBAL_LIMIT_PER_HOUR=4)
    def test_global_hourly_cap(self):
        for i in range(4):
            ContactMessage.objects.create(name="x", contact="x", message="x", ip_hash=f"h{i}")
        self.assertEqual(self.post(self.valid, ajax=True).status_code, 429)

    def test_old_messages_do_not_count(self):
        from datetime import timedelta
        from django.utils import timezone
        from .security import ip_hash as _ip_hash
        for _ in range(3):
            ContactMessage.objects.create(name="x", contact="x", message="x", ip_hash=_ip_hash("127.0.0.1"))
        ContactMessage.objects.update(created_at=timezone.now() - timedelta(hours=2))
        self.assertEqual(self.post(self.valid, ajax=True).status_code, 200)

    def test_ip_is_stored_only_as_hash(self):
        self.post(self.valid, ajax=True)
        msg = ContactMessage.objects.get()
        self.assertEqual(len(msg.ip_hash), 64)
        self.assertNotIn("127.0.0.1", msg.ip_hash)

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get("/uz/contact/").status_code, 405)

    @override_settings(TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="42")
    def test_telegram_notification_sent_when_configured(self):
        fake = mock.MagicMock()
        fake.__enter__.return_value.read.return_value = b'{"ok": true}'
        with mock.patch("portfolio.notifications.urllib.request.urlopen", return_value=fake) as urlopen:
            self.post({**self.valid, "message": "<b>hi</b> & bye"}, ajax=True)
        request = urlopen.call_args[0][0]
        payload = json.loads(request.data)
        self.assertEqual(payload["chat_id"], "42")
        self.assertIn("&lt;b&gt;hi&lt;/b&gt; &amp; bye", payload["text"])  # user text escaped
        self.assertIn("bot123:abc", request.full_url)
        self.assertTrue(ContactMessage.objects.get().telegram_sent)

    @override_settings(TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="42")
    def test_telegram_failure_does_not_break_form(self):
        import urllib.error

        with mock.patch(
            "portfolio.notifications.urllib.request.urlopen",
            side_effect=urllib.error.URLError("down"),
        ), self.assertLogs("portfolio.notifications", level="ERROR"):
            response = self.post(self.valid, ajax=True)
        self.assertTrue(response.json()["ok"])
        self.assertFalse(ContactMessage.objects.get().telegram_sent)

    @override_settings(TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="42")
    def test_any_telegram_network_error_is_swallowed(self):
        # Not only URLError: a reset connection must not 500 a saved message.
        with mock.patch(
            "portfolio.notifications.urllib.request.urlopen",
            side_effect=ConnectionResetError("reset"),
        ), self.assertLogs("portfolio.notifications", level="ERROR"):
            response = self.post(self.valid, ajax=True)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(ContactMessage.objects.count(), 1)


@override_settings(STORAGES=_TEST_STORAGES)
class CaseStudyPageTests(TestCase):
    def test_case_pages_render_in_every_language(self):
        for slug in ("buildops", "oqqushlar", "zebest"):
            p = Project.objects.get(slug=slug)
            for lang in SUPPORTED_LANGUAGES:
                with self.subTest(slug=slug, lang=lang):
                    response = self.client.get(f"/{lang}/work/{slug}/")
                    self.assertEqual(response.status_code, 200)
                    html = response.content.decode()
                    self.assertIn(f'<html lang="{lang}">', html)
                    self.assertIn(f'<link rel="canonical" href="http://testserver/{lang}/work/{slug}/">', html)
                    for code in SUPPORTED_LANGUAGES:
                        self.assertIn(f'hreflang="{code}" href="http://testserver/{code}/work/{slug}/"', html)
                    self.assertIn(STRINGS[lang]["case_solution"], html)
                    first_para = getattr(p, f"problem_{lang}").split("\n\n")[0][:40]
                    self.assertIn(first_para.replace("'", "&#x27;"), html)
                    self.assertIn('property="og:type" content="article"', html)

    def test_next_project_cycles(self):
        html = self.client.get("/en/work/zebest/").content.decode()
        self.assertIn('class="case-next" href="/en/work/buildops/"', html)

    def test_project_without_case_is_404(self):
        self.assertEqual(self.client.get("/uz/work/roma-food/").status_code, 404)
        self.assertEqual(self.client.get("/uz/work/does-not-exist/").status_code, 404)

    def test_case_needs_all_three_languages(self):
        Project.objects.filter(slug="zebest").update(problem_en="", solution_en="")
        self.assertFalse(Project.objects.get(slug="zebest").has_case)
        self.assertEqual(self.client.get("/uz/work/zebest/").status_code, 404)
        self.assertNotIn("/work/zebest/", self.client.get("/sitemap.xml").content.decode())

    @override_settings(DEBUG=False)
    def test_error_pages_have_no_inline_styles(self):
        response = self.client.get("/uz/work/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        html = response.content.decode()
        self.assertNotIn("<style", html)
        self.assertIn('href="/static/portfolio/css/error.css"', html)
        self.assertIn("Content-Security-Policy", response)

    def test_inactive_case_is_404(self):
        Project.objects.filter(slug="zebest").update(is_active=False)
        self.assertEqual(self.client.get("/uz/work/zebest/").status_code, 404)

    def test_case_page_nav_points_back_home(self):
        html = self.client.get("/ru/work/buildops/").content.decode()
        self.assertIn('href="/ru/#about"', html)
        self.assertIn('href="/en/work/buildops/" hreflang="en"', html)  # language switch keeps the page
        commands = json.loads(
            re.search(r'<script id="cmdk-commands" type="application/json">(.*?)</script>', html, re.S).group(1)
        )
        self.assertNotIn("scroll", {c["kind"] for c in commands})


@override_settings(STORAGES=_TEST_STORAGES)
class SecurityTests(TestCase):
    def test_csp_header_and_inline_script_hash_match(self):
        from .security import CONTENT_SECURITY_POLICY, JS_FLAG_HASH, JS_FLAG_SCRIPT

        response = self.client.get("/en/")
        self.assertEqual(response["Content-Security-Policy"], CONTENT_SECURITY_POLICY)
        self.assertIn(JS_FLAG_HASH, response["Content-Security-Policy"])
        self.assertIn("frame-ancestors 'none'", response["Content-Security-Policy"])
        self.assertIn("camera=()", response["Permissions-Policy"])
        # The only inline <script> must be byte-identical to the hashed one.
        html = response.content.decode()
        inline = re.findall(r"<script>(.*?)</script>", html, re.S)
        self.assertEqual(inline, [JS_FLAG_SCRIPT])
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


class CoverCompressionTests(TestCase):
    def setUp(self):
        import tempfile

        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()

    def tearDown(self):
        import shutil

        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def test_large_upload_becomes_small_webp(self):
        import io

        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        buffer = io.BytesIO()
        Image.new("RGB", (3200, 2000), (40, 90, 160)).save(buffer, "PNG")
        p = Project.objects.get(slug="buildops")
        p.cover = SimpleUploadedFile("shot.png", buffer.getvalue(), content_type="image/png")
        p.save()
        p.refresh_from_db()
        self.assertTrue(p.cover.name.endswith(".webp"), p.cover.name)
        with Image.open(p.cover.path) as img:
            self.assertEqual(img.format, "WEBP")
            self.assertEqual(img.size, (1600, 1000))

        # Saving again without a new upload must not re-encode.
        self._assert_second_save_keeps(p)

    def _upload(self, img, fmt="PNG", name="shot.png"):
        import io

        from django.core.files.uploadedfile import SimpleUploadedFile

        buffer = io.BytesIO()
        img.save(buffer, fmt)
        p = Project.objects.get(slug="oqqushlar")
        p.cover = SimpleUploadedFile(name, buffer.getvalue())
        p.save()
        p.refresh_from_db()
        return p

    def test_very_tall_screenshot_is_scaled_not_crashing(self):
        from PIL import Image

        p = self._upload(Image.new("RGB", (1440, 18000), "white"))
        with Image.open(p.cover.path) as img:
            self.assertEqual(img.format, "WEBP")
            self.assertLessEqual(img.height, 16383)

    def test_palette_png_keeps_transparency(self):
        from PIL import Image

        img = Image.new("P", (200, 100), 0)
        img.putpalette([0, 0, 0, 255, 0, 0] + [0] * 762)
        img.info["transparency"] = 0
        p = self._upload(img)
        with Image.open(p.cover.path) as out:
            self.assertEqual(out.mode, "RGBA")

    def test_non_image_is_left_alone(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        p = Project.objects.get(slug="oqqushlar")
        p.cover = SimpleUploadedFile("notes.png", b"not an image")
        p.save()  # must not raise
        self.assertTrue(p.cover.name.endswith(".png"))

    def _assert_second_save_keeps(self, p):
        name = p.cover.name
        p.title_en = "BuildOps"
        p.save()
        p.refresh_from_db()
        self.assertEqual(p.cover.name, name)


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
            "CONTACT_RATE_LIMIT_PER_HOUR": "",
            "TELEGRAM_BOT_TOKEN": "",
        }
        code = (
            "import json, django; django.setup();"
            "from django.conf import settings as s;"
            "print(json.dumps([s.SECRET_KEY, s.DEBUG, s.ALLOWED_HOSTS,"
            " s.SITE_CONTACT_EMAIL, s.CONTACT_RATE_LIMIT_PER_HOUR]))"
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
