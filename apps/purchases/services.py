from django.core.exceptions import ValidationError
from django.db import transaction
from apps.inventory.models import InventoryTransaction, WarehouseInventory
from .models import PurchaseOrder


class PurchaseService:
    @staticmethod
    @transaction.atomic
    def receive_item(item, received_qty, damaged_qty=0, rejected_qty=0, actor=None):
        if received_qty < 0 or damaged_qty < 0 or rejected_qty < 0:
            raise ValidationError("Quantities cannot be negative.")
        accepted_qty = received_qty - damaged_qty - rejected_qty
        if accepted_qty < 0:
            raise ValidationError("Damaged and rejected quantities cannot exceed received quantity.")
        if item.quantity_received + received_qty > item.quantity_ordered:
            raise ValidationError("Cannot receive more than ordered quantity.")

        inventory, _ = WarehouseInventory.objects.select_for_update().get_or_create(
            product=item.product,
            variant=item.variant,
            warehouse=item.purchase_order.warehouse,
            defaults={"physical_stock": 0},
        )
        previous = inventory.physical_stock
        inventory.physical_stock += accepted_qty
        inventory.damaged_stock += damaged_qty
        inventory.save(update_fields=["physical_stock", "damaged_stock"])

        item.quantity_received += received_qty
        item.save(update_fields=["quantity_received"])

        InventoryTransaction.objects.create(
            inventory=inventory,
            transaction_type=InventoryTransaction.Type.PURCHASE,
            previous_quantity=previous,
            quantity_change=accepted_qty,
            new_quantity=inventory.physical_stock,
            reason="Goods receipt",
            reference_type="purchase_order",
            reference_id=str(item.purchase_order_id),
            actor=actor,
        )
        PurchaseService.refresh_status(item.purchase_order)
        return inventory

    @staticmethod
    def refresh_status(purchase_order):
        items = list(purchase_order.items.all())
        if not items:
            return
        if all(item.quantity_received >= item.quantity_ordered for item in items):
            purchase_order.status = PurchaseOrder.Status.RECEIVED
        elif any(item.quantity_received > 0 for item in items):
            purchase_order.status = PurchaseOrder.Status.PARTIALLY_RECEIVED
        purchase_order.save(update_fields=["status"])
