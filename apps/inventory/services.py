from django.core.exceptions import ValidationError
from django.db import transaction
from .models import InventoryTransaction, WarehouseInventory


class InventoryService:
    @staticmethod
    @transaction.atomic
    def reserve(product, variant, quantity, reference_type="", reference_id="", actor=None):
        rows = WarehouseInventory.objects.select_for_update().filter(product=product, variant=variant).order_by("id")
        remaining = quantity
        for inv in rows:
            take = min(inv.available_stock, remaining)
            if take <= 0:
                continue
            previous = inv.reserved_stock
            inv.reserved_stock += take
            inv.save(update_fields=["reserved_stock"])
            InventoryTransaction.objects.create(
                inventory=inv,
                transaction_type=InventoryTransaction.Type.RESERVE,
                previous_quantity=previous,
                quantity_change=take,
                new_quantity=inv.reserved_stock,
                reference_type=reference_type,
                reference_id=reference_id,
                actor=actor,
            )
            remaining -= take
            if remaining == 0:
                return
        raise ValidationError("Insufficient stock.")

    @staticmethod
    @transaction.atomic
    def release(product, variant, quantity, reference_type="", reference_id="", actor=None):
        rows = WarehouseInventory.objects.select_for_update().filter(product=product, variant=variant).order_by("id")
        remaining = quantity
        for inv in rows:
            release_qty = min(inv.reserved_stock, remaining)
            if release_qty <= 0:
                continue
            previous = inv.reserved_stock
            inv.reserved_stock -= release_qty
            inv.save(update_fields=["reserved_stock"])
            InventoryTransaction.objects.create(
                inventory=inv,
                transaction_type=InventoryTransaction.Type.RELEASE,
                previous_quantity=previous,
                quantity_change=-release_qty,
                new_quantity=inv.reserved_stock,
                reference_type=reference_type,
                reference_id=reference_id,
                actor=actor,
            )
            remaining -= release_qty
            if remaining == 0:
                return
