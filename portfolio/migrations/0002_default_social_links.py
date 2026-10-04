from django.db import migrations


DEFAULT_LINKS = [
    {"platform": "github", "url": "https://github.com/ShohzoDev0108", "order": 0},
    {"platform": "instagram", "url": "", "order": 1},
    {"platform": "telegram", "url": "", "order": 2},
    {"platform": "facebook", "url": "", "order": 3},
    {"platform": "x", "url": "", "order": 4},
]


def create_defaults(apps, schema_editor):
    SocialLink = apps.get_model("portfolio", "SocialLink")
    for data in DEFAULT_LINKS:
        SocialLink.objects.get_or_create(
            platform=data["platform"],
            defaults={"url": data["url"], "order": data["order"], "is_active": True},
        )


def remove_defaults(apps, schema_editor):
    SocialLink = apps.get_model("portfolio", "SocialLink")
    SocialLink.objects.filter(
        platform__in=[d["platform"] for d in DEFAULT_LINKS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_defaults, remove_defaults),
    ]
