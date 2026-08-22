from django.db import models


class Payment(models.Model):
    class Method(models.TextChoices):
        COD = "cod", "Cash On Delivery"
        RAZORPAY = "razorpay", "Razorpay"

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.OneToOneField("orders.Order", on_delete=models.PROTECT, related_name="payment")
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    provider_order_id = models.CharField(max_length=120, blank=True)
    provider_payment_id = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class WebhookEventLog(models.Model):
    provider = models.CharField(max_length=40)
    event_id = models.CharField(max_length=160)
    event_type = models.CharField(max_length=120)
    received_at = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(max_length=40, default="received")
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.SET_NULL)
    safe_payload = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        unique_together = ("provider", "event_id")


class CODSettlement(models.Model):
    order = models.OneToOneField("orders.Order", on_delete=models.PROTECT, related_name="cod_settlement")
    collected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remitted_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=40, default="pending")
    settled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)


class PaymentReconciliation(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT, related_name="reconciliation")
    provider_status = models.CharField(max_length=80, blank=True)
    matched = models.BooleanField(default=False)
    difference = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
