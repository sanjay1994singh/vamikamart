from django.db import models
from apps.core.validators import validate_image_upload


class HomeSection(models.Model):
    key = models.CharField(max_length=80)
    title = models.CharField(max_length=160, blank=True)
    content = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)


class Banner(models.Model):
    title = models.CharField(max_length=160)
    image = models.ImageField(upload_to="banners/", blank=True, validators=[validate_image_upload])
    link_url = models.URLField(blank=True)
    placement = models.CharField(max_length=80, default="home")
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
