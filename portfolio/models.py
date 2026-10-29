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
    tech = models.CharField(
        "Texnologiyalar",
        max_length=120,
        blank=True,
        help_text="Vergul bilan, 3 tagacha: Django, PostgreSQL, PWA. Kartada yorliq bo'lib chiqadi.",
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
            "tech": [t.strip() for t in self.tech.split(",") if t.strip()][:3],
        }


class SiteProfile(models.Model):
    """The owner's name — one row, edited in the admin panel."""

    full_name = models.CharField(
        "To'liq ism",
        max_length=120,
        default="Shohzod",
        help_text="Saytda, sarlavhada va Google uchun ma'lumotlarda shu ism ishlatiladi.",
    )

    full_name_ru = models.CharField(
        "Ism (kirillda)",
        max_length=120,
        blank=True,
        help_text="Rus sahifasida ko'rinadigan yozilishi, masalan «Шохзод». Bo'sh bo'lsa, asosiy ism ishlatiladi.",
    )

    class Meta:
        verbose_name = "Sayt profili"
        verbose_name_plural = "Sayt profili"

    def __str__(self):
        return self.full_name

    @classmethod
    def load(cls):
        return cls.objects.first() or cls(full_name="Shohzod")

    def name_for(self, lang):
        """The name as a reader of `lang` writes it (Cyrillic on the Russian page)."""
        if lang == "ru" and self.full_name_ru.strip():
            return self.full_name_ru.strip()
        return self.full_name


class LoginFailure(models.Model):
    """A failed admin login, for throttling password guessing. IP stored only as a hash."""

    ip_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Muvaffaqiyatsiz kirish"
        verbose_name_plural = "Muvaffaqiyatsiz kirishlar"
