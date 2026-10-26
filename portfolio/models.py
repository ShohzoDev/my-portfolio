from urllib.parse import urlsplit

from django.db import models


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

    Every project has its own site, so the portfolio only lists it: name, one
    line about it and its domain — the whole row links to the live site.
    """

    class Status(models.TextChoices):
        LIVE = "live", "Ishlamoqda (production)"
        LAUNCH = "launch", "Ishga tushirilmoqda"
        DEV = "dev", "Ishlab chiqilmoqda"
        TOOL = "tool", "Ichki vosita"

    slug = models.SlugField(max_length=80, unique=True)
    title_uz = models.CharField("Nomi (UZ)", max_length=200)
    title_ru = models.CharField("Nomi (RU)", max_length=200)
    title_en = models.CharField("Nomi (EN)", max_length=200)
    desc_uz = models.CharField("Bir qatorli tavsif (UZ)", max_length=160, help_text="Qisqa: nima va kim uchun.")
    desc_ru = models.CharField("Bir qatorli tavsif (RU)", max_length=160)
    desc_en = models.CharField("Bir qatorli tavsif (EN)", max_length=160)
    link = models.URLField("Sayt havolasi", blank=True, help_text="Butun qator shu saytga olib boradi.")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.LIVE,
        help_text="«Ishlamoqda»dan boshqa holat nom yonida yozib qo'yiladi.",
    )
    is_founder = models.BooleanField("Men asoschiman", default=False, help_text="Nom yonida «Asoschi» belgisi chiqadi.")
    order = models.PositiveIntegerField("Tartib", default=0)
    is_active = models.BooleanField("Saytda ko'rsatilsin", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"

    def __str__(self):
        return self.title_uz

    @property
    def domain(self):
        """https://www.zebest.uz/ -> zebest.uz (what the visitor reads)."""
        if not self.link:
            return ""
        host = urlsplit(self.link).netloc or self.link
        host = host.split("@")[-1].split(":")[0].lower()
        return host[4:] if host.startswith("www.") else host

    def localized(self, lang):
        """Plain dict for the template, resolved to one language."""
        return {
            "slug": self.slug,
            "title": getattr(self, f"title_{lang}", "") or self.title_en,
            "desc": getattr(self, f"desc_{lang}", "") or "",
            "status": self.status,
            "is_founder": self.is_founder,
            "link": self.link,
            "domain": self.domain,
        }


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
        help_text="Tanlansa, holat yozuvi shu loyihaning saytiga havola bo'ladi.",
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
