from django.db import models


class SocialLink(models.Model):
    """
    A social profile shown as an icon in the hero and contact sections.

    Add the real URL from the admin panel whenever it's ready — until
    then the icon still renders on the site, just without a live link.
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
        help_text="To'liq profil manzili. Bo'sh qoldirsangiz, ikonka ko'rinadi lekin bosilmaydi.",
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

    `tier` controls how prominently it is shown: one or two FEATURED projects
    get a full-width card, MAIN projects form the grid, OTHER projects go to
    the compact "Boshqa ishlar" list at the bottom — so a weekend scaffold
    never carries the same visual weight as a production system.
    """

    class Status(models.TextChoices):
        LIVE = "live", "Ishlamoqda (production)"
        DEV = "dev", "Ishlab chiqilmoqda"
        TOOL = "tool", "Ichki vosita"

    class Tier(models.TextChoices):
        FEATURED = "featured", "Asosiy — katta karta"
        MAIN = "main", "Oddiy karta"
        OTHER = "other", "Boshqa ishlar — ixcham ro'yxat"

    slug = models.SlugField(max_length=80, unique=True)
    title_uz = models.CharField("Nomi (UZ)", max_length=200)
    title_ru = models.CharField("Nomi (RU)", max_length=200)
    title_en = models.CharField("Nomi (EN)", max_length=200)
    desc_uz = models.TextField("Tavsif (UZ)")
    desc_ru = models.TextField("Tavsif (RU)")
    desc_en = models.TextField("Tavsif (EN)")
    highlights_uz = models.TextField(
        "Asosiy jihatlar (UZ)",
        blank=True,
        help_text="Har bir qatorga bitta punkt. Faqat 'Asosiy — katta karta' loyihalarda ko'rinadi.",
    )
    highlights_ru = models.TextField("Asosiy jihatlar (RU)", blank=True)
    highlights_en = models.TextField("Asosiy jihatlar (EN)", blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.LIVE)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.MAIN)
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
        help_text="Skrinshot (tavsiya: 1600×1000, JPG/WebP). Katta kartada ko'rinadi.",
    )
    order = models.PositiveIntegerField("Tartib", default=0)
    is_active = models.BooleanField("Saytda ko'rsatilsin", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"

    def __str__(self):
        return self.title_uz

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def localized(self, lang):
        """Plain dict for the template, resolved to one language."""
        highlights = getattr(self, f"highlights_{lang}", "") or ""
        return {
            "slug": self.slug,
            "title": getattr(self, f"title_{lang}"),
            "desc": getattr(self, f"desc_{lang}"),
            "highlights": [h.strip() for h in highlights.splitlines() if h.strip()],
            "status": self.status,
            "tier": self.tier,
            "link": self.link,
            "github": self.github,
            "tags": self.tag_list,
            "cover": self.cover.url if self.cover else "",
        }


class ContactMessage(models.Model):
    """A message sent through the contact form on the site."""

    name = models.CharField("Ism", max_length=120)
    contact = models.CharField("Aloqa (email / Telegram / telefon)", max_length=200)
    message = models.TextField("Xabar", max_length=4000)
    lang = models.CharField("Til", max_length=2, blank=True)
    created_at = models.DateTimeField("Yuborilgan", auto_now_add=True)
    is_read = models.BooleanField("O'qildi", default=False)
    telegram_sent = models.BooleanField("Telegramga yuborildi", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar (aloqa formasi)"

    def __str__(self):
        return f"{self.name} — {self.created_at:%Y-%m-%d %H:%M}"
