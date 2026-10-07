"""Facebook profile is ShohzoDev too. Fills the URL only if it is still empty."""

from django.db import migrations

URL = "https://www.facebook.com/ShohzoDev"


def forwards(apps, schema_editor):
    SocialLink = apps.get_model("portfolio", "SocialLink")
    link = SocialLink.objects.filter(platform="facebook").first()
    if link is None:
        SocialLink.objects.create(platform="facebook", url=URL, order=3, is_active=True)
    elif not link.url:
        link.url = URL
        link.save(update_fields=["url"])


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0008_shohzodev_handle"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
