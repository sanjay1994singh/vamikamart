from django.conf import settings
from django.db import models


class CheckoutQuote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=80, blank=True, db_index=True)
    cart = models.ForeignKey("carts.Cart", on_delete=models.CASCADE)
    totals = models.JSONField(default=dict)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class IdempotencyKey(models.Model):
    key = models.CharField(max_length=120, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    request_hash = models.CharField(max_length=128, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
