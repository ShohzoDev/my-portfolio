"""
Projects become a plain list of links: every project has its own site, so
the portfolio shows only the name, one line about it and the domain.

- BuildOps is now BuildBest (buildbest.uz),
- Zebest links to zebest.uz and is live (public site with sign-up),
- every listed project gets a short one-line description,
- projects without a public site (LingvoApp, the bots) are hidden — they can
  be switched back on in the admin panel,
- the hero status line follows Zebest's launch.

Uzbek text is written in the old spelling and converted with to_new_latin,
the same way as the rest of the site.
"""

from django.db import migrations

from portfolio.uz_alphabet import to_new_latin

PROJECTS = {
    "zebest": {
        "order": 1,
        "link": "https://zebest.uz",
        "status": "live",
        "title": {"uz": "Zebest", "ru": "Zebest", "en": "Zebest"},
        "desc": {
            "uz": "Restoran va kafelar uchun boshqaruv tizimi — QR-menyudan yetkazib berishgacha",
            "ru": "Система управления для ресторанов и кафе — от QR-меню до доставки",
            "en": "Management system for restaurants and cafés, from QR menus to delivery",
        },
    },
    "buildbest": {
        "order": 2,
        "link": "https://buildbest.uz",
        "status": "live",
        "title": {"uz": "BuildBest", "ru": "BuildBest", "en": "BuildBest"},
        "desc": {
            "uz": "Qurilish kompaniyalari uchun boshqaruv tizimi — obyekt, xodim, texnika va moliya",
            "ru": "Система управления для строительных компаний — объекты, сотрудники, техника и финансы",
            "en": "Management system for construction companies: sites, staff, machinery and finance",
        },
    },
    "oqqushlar": {
        "order": 3,
        "link": "https://oqqushlar.uz",
        "status": "live",
        "title": {"uz": "Oqqushlar", "ru": "Oqqushlar", "en": "Oqqushlar"},
        "desc": {
            "uz": "To'y va marosimlar uchun onlayn taklifnomalar",
            "ru": "Онлайн-приглашения на свадьбы и торжества",
            "en": "Online invitations for weddings and celebrations",
        },
    },
    "geodezistman": {
        "order": 4,
        "link": "https://geodezistman.uz",
        "status": "live",
        "title": {"uz": "Geodezistman", "ru": "Geodezistman", "en": "Geodezistman"},
        "desc": {
            "uz": "Geodezistlar uchun onlayn kurslar platformasi",
            "ru": "Платформа онлайн-курсов для геодезистов",
            "en": "Online course platform for land surveyors",
        },
    },
    "roma-food": {
        "order": 5,
        "link": "https://romafood.pythonanywhere.com",
        "status": "live",
        "title": {"uz": "Roma Food", "ru": "Roma Food", "en": "Roma Food"},
        "desc": {
            "uz": "Fastfud restorani uchun QR-menyu",
            "ru": "QR-меню для фастфуд-ресторана",
            "en": "QR menu for a fast-food restaurant",
        },
    },
}

HIDE = ("lingvoapp", "english-bot", "n8n-workflows", "geo-portfolio")

OLD_NOW = {
    "uz": "Hozir: Zebest restoran platformasini ishga tushiryapman",
    "ru": "Сейчас: запускаю Zebest — платформу для ресторанов",
    "en": "Now: launching Zebest, a platform for restaurants",
}
NEW_NOW = {
    "uz": "Hozir: Zebest restoran platformasini rivojlantiryapman",
    "ru": "Сейчас: развиваю Zebest — платформу для ресторанов",
    "en": "Now: building Zebest, a platform for restaurants",
}

DESC_MAX = 160  # the description becomes a one-line CharField in 0014


def forwards(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")
    SiteProfile = apps.get_model("portfolio", "SiteProfile")

    if not Project.objects.filter(slug="buildbest").exists():
        Project.objects.filter(slug="buildops").update(slug="buildbest")

    for slug, data in PROJECTS.items():
        project = Project.objects.filter(slug=slug).first()
        if project is None:
            project = Project(slug=slug)
        project.order = data["order"]
        project.link = data["link"]
        project.status = data["status"]
        project.is_active = True
        for lang in ("uz", "ru", "en"):
            title, desc = data["title"][lang], data["desc"][lang]
            if lang == "uz":
                desc = to_new_latin(desc)
            setattr(project, f"title_{lang}", title)
            setattr(project, f"desc_{lang}", desc)
        project.save()

    Project.objects.filter(slug__in=HIDE).update(is_active=False)

    # Anything left (an admin-made project) must fit the one-line field.
    for project in Project.objects.all():
        changed = False
        for lang in ("uz", "ru", "en"):
            value = " ".join((getattr(project, f"desc_{lang}") or "").split())
            if len(value) > DESC_MAX:
                value = value[: DESC_MAX - 1].rstrip() + "…"
            if value != getattr(project, f"desc_{lang}"):
                setattr(project, f"desc_{lang}", value)
                changed = True
        if changed:
            project.save()

    profile = SiteProfile.objects.first()
    if profile is not None:
        for lang in ("uz", "ru", "en"):
            current = (getattr(profile, f"now_{lang}") or "").strip()
            old = OLD_NOW[lang]
            if current in (old, to_new_latin(old)):
                new = NEW_NOW[lang]
                setattr(profile, f"now_{lang}", to_new_latin(new) if lang == "uz" else new)
        if profile.now_project_id is None:
            profile.now_project = Project.objects.filter(slug="zebest").first()
        profile.save()


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0012_uz_new_alphabet"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
