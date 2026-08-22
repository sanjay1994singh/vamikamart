from django.db import models


class Shipment(models.Model):
    order = models.OneToOneField("orders.Order", on_delete=models.PROTECT, related_name="shipment")
    carrier = models.CharField(max_length=80, blank=True)
    awb = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=40, default="pending")
    tracking_url = models.URLField(blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)


class ShippingManifest(models.Model):
    manifest_number = models.CharField(max_length=40, unique=True)
    carrier = models.CharField(max_length=80)
    shipments = models.ManyToManyField(Shipment, related_name="manifests")
    created_at = models.DateTimeField(auto_now_add=True)


class NDRRecord(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.PROTECT, related_name="ndr_records")
    reason = models.CharField(max_length=220)
    action = models.CharField(max_length=80, default="reattempt")
    status = models.CharField(max_length=40, default="open")
    created_at = models.DateTimeField(auto_now_add=True)


class RTORecord(models.Model):
    shipment = models.OneToOneField(Shipment, on_delete=models.PROTECT, related_name="rto_record")
    reason = models.CharField(max_length=220, blank=True)
    received_at_warehouse = models.DateTimeField(null=True, blank=True)
    inventory_adjusted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
