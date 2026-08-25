from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator


class MobileAppBuild(models.Model):
    class Platform(models.TextChoices):
        ANDROID = "android", "Android"
        IOS = "ios", "iOS"

    class Track(models.TextChoices):
        TESTING = "testing", "Testing"
        PRODUCTION = "production", "Production"

    platform = models.CharField(max_length=20, choices=Platform.choices, default=Platform.ANDROID)
    track = models.CharField(max_length=20, choices=Track.choices, default=Track.TESTING)
    version_name = models.CharField(max_length=40)
    version_code = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    build_file = models.FileField(
        upload_to="mobile-builds/%Y/%m/",
        validators=[FileExtensionValidator(["apk", "aab"])],
    )
    release_notes = models.TextField(blank=True)
    force_update = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_code", "-created_at"]
        indexes = [
            models.Index(fields=["platform", "track", "active", "-version_code"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["platform", "track", "version_code"], name="unique_mobile_build_version"),
        ]

    def __str__(self):
        return f"{self.get_platform_display()} {self.get_track_display()} {self.version_name} ({self.version_code})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        latest = (
            type(self).objects.filter(platform=self.platform, track=self.track)
            .order_by("-version_code", "-created_at", "-id")
            .first()
        )
        if not latest:
            return
        older_builds = list(type(self).objects.filter(platform=self.platform, track=self.track).exclude(pk=latest.pk).exclude(build_file=""))
        type(self).objects.filter(pk__in=[build.pk for build in older_builds]).update(active=False, build_file="")
        for build in older_builds:
            build.build_file.storage.delete(build.build_file.name)
        type(self).objects.filter(platform=self.platform, track=self.track).exclude(pk=latest.pk).update(active=False)
        if not latest.active:
            type(self).objects.filter(pk=latest.pk).update(active=True)
