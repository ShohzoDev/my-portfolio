"""
Uzbek content -> updated Latin alphabet (Sh->Ş, Ch->Ç, O'->Ö, G'->Ğ).

Converts every Uzbek field of projects and the site profile. Project and
brand names keep their own spelling (see portfolio/uz_alphabet.py). The
conversion is idempotent, so re-running it is harmless.
"""

from django.db import migrations

from portfolio.uz_alphabet import to_new_latin

PROJECT_FIELDS = ("title", "desc", "facts", "problem", "solution", "result", "highlights")
PROFILE_FIELDS = ("about", "now")


def forwards(apps, schema_editor):
    Project = apps.get_model("portfolio", "Project")
    SiteProfile = apps.get_model("portfolio", "SiteProfile")

    for project in Project.objects.all():
        for field in PROJECT_FIELDS:
            name = f"{field}_uz"
            setattr(project, name, to_new_latin(getattr(project, name)))
        project.save(update_fields=[f"{f}_uz" for f in PROJECT_FIELDS])

    for profile in SiteProfile.objects.all():
        for field in PROFILE_FIELDS:
            name = f"{field}_uz"
            setattr(profile, name, to_new_latin(getattr(profile, name)))
        profile.save(update_fields=[f"{f}_uz" for f in PROFILE_FIELDS])


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0011_zebest_founder"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
