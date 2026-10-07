"""
Shohzod is the founder of Zebest and the platform is about to launch:
- Zebest gets the founder flag (badge on the card, founder role on its page),
- the hero status line points to Zebest,
- the case-study result reflects the near-launch state.
Admin edits are never overwritten (texts change only if still the seed value).
"""

from django.db import migrations

NOW = {
    "uz": "Hozir: Zebest restoran platformasini ishga tushiryapman",
    "ru": "Сейчас: запускаю Zebest — платформу для ресторанов",
    "en": "Now: launching Zebest, a platform for restaurants",
}

OLD_RESULT = {
    "uz": "Platforma ishga tushirish bosqichida: asosiy domen va har bir restoran uchun wildcard subdomenlar ulanmoqda.",
    "ru": "Платформа на этапе запуска: подключаются основной домен и wildcard-поддомены для каждого ресторана.",
    "en": "The platform is in its launch phase: the main domain and wildcard subdomains for each restaurant are being connected.",
}
NEW_RESULT = {
    "uz": (
        "Platforma ishga tushish arafasida: asosiy funksiyalar tayyor, asosiy domen va har bir restoran "
        "uchun wildcard subdomenlar ulanmoqda."
    ),
    "ru": (
        "Платформа почти готова к запуску: основной функционал готов, подключаются основной домен и "
        "wildcard-поддомены для каждого ресторана."
    ),
    "en": (
        "The platform is about to launch: the core features are done, and the main domain plus a wildcard "
        "subdomain for each restaurant are being connected."
    ),
}


def forwards(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")
    SiteProfile = apps.get_model("portfolio", "SiteProfile")

    zebest = Project.objects.filter(slug="zebest").first()
    if zebest is None:
        return
    zebest.is_founder = True
    for lang in ("uz", "ru", "en"):
        if getattr(zebest, f"result_{lang}").strip() == OLD_RESULT[lang]:
            setattr(zebest, f"result_{lang}", NEW_RESULT[lang])
    zebest.save()

    profile = SiteProfile.objects.first()
    if profile is not None and not (profile.now_uz or profile.now_ru or profile.now_en):
        profile.now_uz, profile.now_ru, profile.now_en = NOW["uz"], NOW["ru"], NOW["en"]
        profile.now_project = zebest
        profile.save()


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0010_founder_and_now_status"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
