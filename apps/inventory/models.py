from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Warehouse(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=32, unique=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pin = models.CharField(max_length=12, blank=True)
    contact = models.CharField(max_length=40, blank=True)
    active = models.BooleanField(default=True)


class WarehouseInventory(models.Model):
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT)
    variant = models.ForeignKey("catalog.ProductVariant", null=True, blank=True, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    physical_stock = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)
    returned_stock = models.PositiveIntegerField(default=0)
    damaged_stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "variant", "warehouse")

    @property
    def available_stock(self):
        return max(self.physical_stock - self.reserved_stock - self.damaged_stock, 0)


class InventoryTransaction(models.Model):
    class Type(models.TextChoices):
        PURCHASE = "purchase", "Purchase"
        SALE = "sale", "Sale"
        RESERVE = "reserve", "Reserve"
        RELEASE = "release", "Release"
        RETURN = "return", "Return"
        CANCEL = "cancel", "Cancel"
        DAMAGE = "damage", "Damage"
        RESTOCK = "restock", "Restock"
        MANUAL_ADJUSTMENT = "manual_adjustment", "Manual Adjustment"
        RTO = "rto", "RTO"

    inventory = models.ForeignKey(WarehouseInventory, on_delete=models.PROTECT, related_name="transactions")
    transaction_type = models.CharField(max_length=32, choices=Type.choices)
    previous_quantity = models.IntegerField()
    quantity_change = models.IntegerField(validators=[MinValueValidator(-999999)])
    new_quantity = models.IntegerField()
    reason = models.CharField(max_length=220, blank=True)
    reference_type = models.CharField(max_length=80, blank=True)
    reference_id = models.CharField(max_length=80, blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class StockNotificationRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    variant = models.ForeignKey("catalog.ProductVariant", null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product", "variant")
