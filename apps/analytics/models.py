from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=120)
    entity = models.CharField(max_length=120)
    object_id = models.CharField(max_length=80, blank=True)
    previous_value = models.JSONField(default=dict, blank=True)
    new_value = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OperationalExpense(models.Model):
    class Category(models.TextChoices):
        SHIPPING = "shipping", "Shipping"
        PACKAGING = "packaging", "Packaging"
        PAYMENT_GATEWAY = "payment_gateway", "Payment Gateway"
        MARKETING = "marketing", "Marketing"
        OTHER = "other", "Other"

    category = models.CharField(max_length=32, choices=Category.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=220, blank=True)
    incurred_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class CustomerTimelineEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="timeline_events")
    event_type = models.CharField(max_length=80)
    title = models.CharField(max_length=160)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CustomerMetricSnapshot(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="metric_snapshot")
    order_count = models.PositiveIntegerField(default=0)
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_order_at = models.DateTimeField(null=True, blank=True)
    support_ticket_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class ActionQueueItem(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        NORMAL = 2, "Normal"
        HIGH = 3, "High"

    title = models.CharField(max_length=180)
    queue = models.CharField(max_length=80)
    priority = models.IntegerField(choices=Priority.choices, default=Priority.NORMAL)
    entity = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=80, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
