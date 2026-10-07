import io
import os

from django.core.files.base import ContentFile
from django.db import models

# Uploaded covers are re-encoded to this width (px) and WebP quality, so an
# 8 MB phone screenshot never reaches visitors.
COVER_MAX_WIDTH = 1600
COVER_WEBP_QUALITY = 82


class SocialLink(models.Model):
    """
    A social profile shown as an icon in the hero and contact sections.

    Only profiles with a URL are shown publicly — a row of dead icons reads
    as an unfinished site. Fill the URL in the admin panel and it appears.
    The Telegram profile also becomes the main "write on Telegram" button.
    """

    class Platform(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        TELEGRAM = "telegram", "Telegram"
        FACEBOOK = "facebook", "Facebook"
        X = "x", "X (Twitter)"
        LINKEDIN = "linkedin", "LinkedIn"
        YOUTUBE = "youtube", "YouTube"
        GITHUB = "github", "GitHub"
        OTHER = "other", "Boshqa"

    platform = models.CharField(max_length=20, choices=Platform.choices)
    label = models.CharField(
        max_length=50,
        blank=True,
        help_text="Faqat platform 'Boshqa' bo'lsa ko'rinadi (masalan: 'Behance').",
    )
    url = models.URLField(
        blank=True,
        help_text="To'liq profil manzili. Bo'sh bo'lsa, ikonka saytda ko'rinmaydi.",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Ijtimoiy tarmoq"
        verbose_name_plural = "Ijtimoiy tarmoqlar"

    def __str__(self):
        return self.label or self.get_platform_display()

    @property
    def display_name(self):
        return self.label or self.get_platform_display()

    @property
    def has_link(self):
        return bool(self.url)


class Project(models.Model):
    """
    A portfolio project, edited from the admin panel in all three languages.

    `tier` controls how prominently it is shown: FEATURED projects (keep it to
    about three) get a card in "Tanlangan ishlar"; everything else goes to the
    one-line "Boshqa ishlar" list — so a weekend scaffold never carries the
    same visual weight as a production system.

    A project with case-study text (task / solution / result) also gets its
    own page at /<lang>/work/<slug>/ — the link to send a client.
    """

    class Status(models.TextChoices):
        LIVE = "live", "Ishlamoqda (production)"
        LAUNCH = "launch", "Ishga tushirilmoqda"
        DEV = "dev", "Ishlab chiqilmoqda"
        TOOL = "tool", "Ichki vosita"

    class Tier(models.TextChoices):
        FEATURED = "featured", "Tanlangan — karta"
        MAIN = "main", "Boshqa ishlar (eski: oddiy karta)"
        OTHER = "other", "Boshqa ishlar — ixcham ro'yxat"

    slug = models.SlugField(max_length=80, unique=True)
    title_uz = models.CharField("Nomi (UZ)", max_length=200)
    title_ru = models.CharField("Nomi (RU)", max_length=200)
    title_en = models.CharField("Nomi (EN)", max_length=200)
    desc_uz = models.TextField("Qisqa tavsif (UZ)", help_text="Bitta jumla — kartada va ro'yxatda ko'rinadi.")
    desc_ru = models.TextField("Qisqa tavsif (RU)")
    desc_en = models.TextField("Qisqa tavsif (EN)")
    facts_uz = models.TextField(
        "Raqamlar (UZ)",
        blank=True,
        help_text="Har qatorga bitta qisqa fakt, 3 tagacha: '258 test', '8 til'. Kartada ko'rinadi.",
    )
    facts_ru = models.TextField("Raqamlar (RU)", blank=True)
    facts_en = models.TextField("Raqamlar (EN)", blank=True)
    problem_uz = models.TextField("Case: vazifa (UZ)", blank=True)
    problem_ru = models.TextField("Case: vazifa (RU)", blank=True)
    problem_en = models.TextField("Case: vazifa (EN)", blank=True)
    solution_uz = models.TextField(
        "Case: yechim (UZ)",
        blank=True,
        help_text="Bo'sh qatorlar bilan xatboshilarga ajrating.",
    )
    solution_ru = models.TextField("Case: yechim (RU)", blank=True)
    solution_en = models.TextField("Case: yechim (EN)", blank=True)
    result_uz = models.TextField("Case: natija (UZ)", blank=True)
    result_ru = models.TextField("Case: natija (RU)", blank=True)
    result_en = models.TextField("Case: natija (EN)", blank=True)
    highlights_uz = models.TextField(
        "Asosiy jihatlar (UZ)",
        blank=True,
        help_text="Har bir qatorga bitta punkt. Loyihaning alohida (case) sahifasida ko'rinadi.",
    )
    highlights_ru = models.TextField("Asosiy jihatlar (RU)", blank=True)
    highlights_en = models.TextField("Asosiy jihatlar (EN)", blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.LIVE)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.OTHER)
    link = models.URLField("Sayt havolasi", blank=True)
    github = models.URLField("GitHub havolasi", blank=True)
    tags = models.CharField(
        "Texnologiyalar",
        max_length=255,
        blank=True,
        help_text="Vergul bilan ajrating: Django, PostgreSQL, Nginx",
    )
    cover = models.ImageField(
        "Muqova rasmi",
        upload_to="projects/",
        blank=True,
        help_text="Skrinshot (tavsiya: 1600×1000). Avtomatik ravishda 1600px WebP'ga siqiladi. "
        "Case sahifasida ko'rinadi.",
    )
    order = models.PositiveIntegerField("Tartib", default=0)
    is_active = models.BooleanField("Saytda ko'rsatilsin", default=True)
    is_founder = models.BooleanField(
        "Men asoschiman",
        default=False,
        help_text="Kartada «Asoschi» belgisi chiqadi, case sahifasida rol «Asoschi» deb ko'rsatiladi.",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"

    def __str__(self):
        return self.title_uz

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    @property
    def has_case(self):
        """A case page exists only when it is written in all three languages
        (otherwise /ru/ or /en/ would show an empty page)."""
        return all(
            (getattr(self, f"problem_{lang}") or "").strip() or (getattr(self, f"solution_{lang}") or "").strip()
            for lang in ("uz", "ru", "en")
        )

    @staticmethod
    def _lines(text):
        return [line.strip() for line in (text or "").splitlines() if line.strip()]

    @staticmethod
    def _paragraphs(text):
        return [" ".join(p.split()) for p in (text or "").replace("\r\n", "\n").split("\n\n") if p.strip()]

    def localized(self, lang):
        """Plain dict for the template, resolved to one language."""
        def field(name):
            return getattr(self, f"{name}_{lang}", "") or ""

        return {
            "slug": self.slug,
            "title": field("title"),
            "desc": field("desc"),
            "facts": self._lines(field("facts"))[:3],
            "highlights": self._lines(field("highlights")),
            "problem": self._paragraphs(field("problem")),
            "solution": self._paragraphs(field("solution")),
            "result": self._paragraphs(field("result")),
            "has_case": self.has_case,
            "is_founder": self.is_founder,
            "status": self.status,
            "tier": self.tier,
            "link": self.link,
            "github": self.github,
            "tags": self.tag_list,
            "cover": self.cover.url if self.cover else "",
        }

    def save(self, *args, **kwargs):
        self._compress_cover()
        super().save(*args, **kwargs)

    def _compress_cover(self):
        """Re-encode a freshly uploaded cover to WebP, max COVER_MAX_WIDTH wide."""
        cover = self.cover
        if not cover or getattr(cover, "_committed", True):
            return  # nothing new uploaded
        from PIL import Image, ImageOps

        try:
            cover.seek(0)
            img = Image.open(cover)
            img = ImageOps.exif_transpose(img)  # also drops EXIF (GPS etc.)
        except Exception:  # noqa: BLE001 — not an image Pillow can read; leave as is
            return
        if img.mode not in ("RGB", "RGBA"):
            has_alpha = "A" in img.getbands() or "transparency" in img.info
            img = img.convert("RGBA" if has_alpha else "RGB")
        # WebP can't exceed 16383 px on either side (very tall full-page shots).
        img.thumbnail((COVER_MAX_WIDTH, 16383), Image.LANCZOS)
        buffer = io.BytesIO()
        try:
            img.save(buffer, "WEBP", quality=COVER_WEBP_QUALITY, method=6)
        except (OSError, ValueError):
            return  # keep the original upload rather than failing the save
        stem = os.path.splitext(os.path.basename(cover.name))[0] or self.slug or "cover"
        self.cover = ContentFile(buffer.getvalue(), name=f"{stem}.webp")


class SiteProfile(models.Model):
    """
    The owner's name and About text — one row, edited in the admin panel
    (no code change needed to rewrite the About section).
    """

    full_name = models.CharField(
        "To'liq ism",
        max_length=120,
        default="Shohzod",
        help_text="Saytda, sarlavhada va Google uchun ma'lumotlarda shu ism ishlatiladi.",
    )
    about_uz = models.TextField("Men haqimda (UZ)", help_text="2–3 jumla. Bo'sh qator — yangi xatboshi.")
    about_ru = models.TextField("Men haqimda (RU)")
    about_en = models.TextField("Men haqimda (EN)")
    now_uz = models.CharField(
        "Hozir nima qilyapman (UZ)",
        max_length=120,
        blank=True,
        help_text="Hero'dagi holat yozuvi. Bo'sh bo'lsa: «Yangi loyihalarga ochiqman».",
    )
    now_ru = models.CharField("Hozir nima qilyapman (RU)", max_length=120, blank=True)
    now_en = models.CharField("Hozir nima qilyapman (EN)", max_length=120, blank=True)
    now_project = models.ForeignKey(
        "Project",
        verbose_name="Holat yozuvi havolasi",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Tanlansa, holat yozuvi shu loyihaning case sahifasiga havola bo'ladi.",
    )

    class Meta:
        verbose_name = "Sayt profili"
        verbose_name_plural = "Sayt profili"

    def __str__(self):
        return self.full_name

    @classmethod
    def load(cls):
        profile = cls.objects.first()
        return profile or cls(full_name="Shohzod", about_uz="", about_ru="", about_en="")

    def about_paragraphs(self, lang):
        text = getattr(self, f"about_{lang}", "") or ""
        return [" ".join(p.split()) for p in text.replace("\r\n", "\n").split("\n\n") if p.strip()]


class LoginFailure(models.Model):
    """A failed admin login, for throttling password guessing. IP stored only as a hash."""

    ip_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Muvaffaqiyatsiz kirish"
        verbose_name_plural = "Muvaffaqiyatsiz kirishlar"


class ContactMessage(models.Model):
    """A message sent through the contact form on the site."""

    name = models.CharField("Ism", max_length=120)
    contact = models.CharField("Aloqa (email / Telegram / telefon)", max_length=200)
    message = models.TextField("Xabar", max_length=4000)
    lang = models.CharField("Til", max_length=2, blank=True)
    # Salted hash of the sender's IP — enough to rate-limit per sender
    # (works across all gunicorn workers, unlike an in-memory cache) without
    # storing the raw IP address.
    ip_hash = models.CharField(max_length=64, blank=True, db_index=True, editable=False)
    created_at = models.DateTimeField("Yuborilgan", auto_now_add=True)
    is_read = models.BooleanField("O'qildi", default=False)
    telegram_sent = models.BooleanField("Telegramga yuborildi", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar (aloqa formasi)"

    def __str__(self):
        return f"{self.name} — {self.created_at:%Y-%m-%d %H:%M}"
