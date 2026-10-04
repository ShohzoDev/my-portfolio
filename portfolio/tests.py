import json
import re
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .content import STRINGS, SUPPORTED_LANGUAGES, localized_skills, plural_key
from .models import ContactMessage, Project, SocialLink

# The index template uses {% static %}, and production uses WhiteNoise's
# manifest storage (hashed filenames, requires `collectstatic`). Django's test
# runner forces DEBUG=False, which makes that storage strict about missing
# manifest entries — so tests that render the real template use the plain
# storage instead. Unrelated to what these tests verify.
_TEST_STORAGES = {
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
    def test_seed_migration_created_all_projects_with_tiers(self):
        self.assertEqual(Project.objects.count(), 8)
        self.assertEqual(Project.objects.get(slug="buildops").tier, Project.Tier.FEATURED)
        self.assertEqual(
            set(Project.objects.filter(tier=Project.Tier.OTHER).values_list("slug", flat=True)),
            {"english-bot", "n8n-workflows"},
        )

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
        self.assertEqual(len(data["highlights"]), 5)
        self.assertEqual(data["cover"], "")


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
        self.assertIn("https://github.com/ShohzoDev0108", data["sameAs"])

    def test_content_is_server_rendered(self):
        html = self.get()
        self.assertIn("BuildOps", html)
        self.assertIn("full-stack dasturchiman", html)  # about text (no apostrophe — autoescape)

    def test_project_tiers_render_in_their_sections(self):
        html = self.get("en")
        self.assertIn('class="project-card featured', html)
        self.assertIn('id="p-buildops"', html)
        other = html[html.index('class="other-list"'):]
        self.assertIn('id="p-english-bot"', other)
        self.assertIn('id="p-n8n-workflows"', other)

    def test_badge_counts_only_live_projects(self):
        live = Project.objects.filter(is_active=True, status=Project.Status.LIVE).count()
        html = self.get("ru")
        self.assertIn(f"<strong>{live}</strong>", html)
        self.assertIn(STRINGS["ru"][plural_key("ru", live)], html)

    def test_inactive_project_is_hidden(self):
        Project.objects.filter(slug="lingvoapp").update(is_active=False)
        self.assertNotIn('id="p-lingvoapp"', self.get())

    def test_unlinked_social_icon_has_role_img(self):
        html = self.get()
        self.assertIn('class="social-icon unlinked" role="img"', html)

    def test_command_palette_data(self):
        html = self.get("en")
        match = re.search(r'<script id="cmdk-commands" type="application/json">(.*?)</script>', html, re.S)
        commands = json.loads(match.group(1))
        kinds = {c["kind"] for c in commands}
        self.assertEqual(kinds, {"scroll", "href", "copy"})
        current = [c for c in commands if c.get("current")]
        self.assertEqual([c["href"] for c in current], ["/en/"])

    def test_robots_and_sitemap(self):
        robots = self.client.get(reverse("portfolio:robots_txt")).content.decode()
        self.assertIn("Disallow: /admin/", robots)
        self.assertIn("Sitemap: http://testserver/sitemap.xml", robots)
        sitemap = self.client.get(reverse("portfolio:sitemap_xml")).content.decode()
        for lang in SUPPORTED_LANGUAGES:
            self.assertIn(f"<loc>http://testserver/{lang}/</loc>", sitemap)
        self.assertIn('hreflang="x-default"', sitemap)


@override_settings(STORAGES=_TEST_STORAGES, CONTACT_RATE_LIMIT_PER_HOUR=3)
class ContactFormTests(TestCase):
    valid = {"name": "Ali", "contact": "@ali", "message": "Salom, loyiha bor."}

    def setUp(self):
        cache.clear()

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
        response = self.post({**self.valid, "website": "http://spam.example"}, ajax=True)
        self.assertTrue(response.json()["ok"])
        self.assertFalse(ContactMessage.objects.exists())

    def test_rate_limit(self):
        for _ in range(3):
            self.assertEqual(self.post(self.valid, ajax=True).status_code, 200)
        blocked = self.post(self.valid, ajax=True)
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(ContactMessage.objects.count(), 3)

    def test_rate_limit_is_per_client_ip(self):
        for _ in range(3):
            self.post(self.valid, ajax=True, HTTP_X_REAL_IP="1.1.1.1")
        other = self.post(self.valid, ajax=True, HTTP_X_REAL_IP="2.2.2.2")
        self.assertEqual(other.status_code, 200)

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
        ):
            response = self.post(self.valid, ajax=True)
        self.assertTrue(response.json()["ok"])
        self.assertFalse(ContactMessage.objects.get().telegram_sent)


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
