# Generated manually for mobile build upload support.

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MobileAppBuild",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("platform", models.CharField(choices=[("android", "Android"), ("ios", "iOS")], default="android", max_length=20)),
                ("track", models.CharField(choices=[("testing", "Testing"), ("production", "Production")], default="testing", max_length=20)),
                ("version_name", models.CharField(max_length=40)),
                ("version_code", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("build_file", models.FileField(upload_to="mobile-builds/%Y/%m/", validators=[django.core.validators.FileExtensionValidator(["apk", "aab"])])),
                ("release_notes", models.TextField(blank=True)),
                ("force_update", models.BooleanField(default=False)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-version_code", "-created_at"],
                "indexes": [models.Index(fields=["platform", "track", "active", "-version_code"], name="core_mobile_platfor_65f6c3_idx")],
                "constraints": [models.UniqueConstraint(fields=("platform", "track", "version_code"), name="unique_mobile_build_version")],
            },
        ),
    ]
