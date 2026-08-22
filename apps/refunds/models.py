from django.db import models


class Refund(models.Model):
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="refunds")
    payment = models.ForeignKey("payments.Payment", null=True, blank=True, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=40, default="pending")
    provider_refund_id = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RefundReconciliation(models.Model):
    refund = models.OneToOneField(Refund, on_delete=models.PROTECT, related_name="reconciliation")
    provider_status = models.CharField(max_length=80, blank=True)
    reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
