"""
GitHub username changed ShohzoDev0108 -> ShohzoDev (2026-10-07), and the
same handle is used on Telegram, Instagram and X. Updates existing links and
fills the empty social profiles (never overwrites a URL set in the admin).
"""

from django.db import migrations

OLD = "github.com/ShohzoDev0108"
NEW = "github.com/ShohzoDev"

PROFILES = {
    "telegram": "https://t.me/ShohzoDev",
    "instagram": "https://www.instagram.com/ShohzoDev/",
    "x": "https://x.com/ShohzoDev",
}


def forwards(apps, schema_editor):
    SocialLink = apps.get_model("portfolio", "SocialLink")
    Project = apps.get_model("portfolio", "Project")

    for link in SocialLink.objects.filter(url__contains=OLD):
        link.url = link.url.replace(OLD, NEW)
        link.save(update_fields=["url"])

    for platform, url in PROFILES.items():
        link = SocialLink.objects.filter(platform=platform).first()
        if link is None:
            SocialLink.objects.create(platform=platform, url=url, is_active=True)
        elif not link.url:
            link.url = url
            link.save(update_fields=["url"])

    for project in Project.objects.all():
        changed = False
        for field in ("github", "link"):
            value = getattr(project, field)
            if OLD in value:
                setattr(project, field, value.replace(OLD, NEW))
                changed = True
        if changed:
            project.save(update_fields=["github", "link"])


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0007_compact_portfolio_content"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
