from django.conf import settings
from django.db import models
from apps.core.validators import validate_image_upload


class BusinessProfile(models.Model):
    store_name = models.CharField(max_length=160)
    legal_name = models.CharField(max_length=200, blank=True)
    logo = models.ImageField(upload_to="business/", blank=True, validators=[validate_image_upload])
    favicon = models.ImageField(upload_to="business/", blank=True, validators=[validate_image_upload])
    support_phone = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    support_email = models.EmailField(blank=True)
    business_address = models.TextField(blank=True)
    return_address = models.TextField(blank=True)
    gst_number = models.CharField(max_length=32, blank=True)
    pan = models.CharField(max_length=20, blank=True)
    cin = models.CharField(max_length=32, blank=True)
    currency = models.CharField(max_length=8, default="INR")
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    is_active = models.BooleanField(default=True)


class StaffRole(models.Model):
    name = models.CharField(max_length=80, unique=True)
    permissions = models.JSONField(default=list, blank=True)


class StaffProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(StaffRole, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
