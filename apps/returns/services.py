from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from apps.analytics.audit import AuditService
from apps.inventory.models import InventoryTransaction, WarehouseInventory


class ReturnService:
    @staticmethod
    def is_eligible(order_item):
        product = order_item.product
        if not product.returnable:
            return False
        delivered_at = getattr(getattr(order_item.order, "shipment", None), "delivered_at", None)
        if not delivered_at:
            return False
        return timezone.now() <= delivered_at + timezone.timedelta(days=product.return_window_days)

    @staticmethod
    def validate_request(return_request):
        if return_request.order.user_id != return_request.user_id:
            raise ValidationError("Return request does not belong to this customer.")
        return True

    @staticmethod
    @transaction.atomic
    def approve(return_request, actor=None):
        ReturnService.validate_request(return_request)
        return_request.status = "approved"
        return_request.save(update_fields=["status"])
        AuditService.log("return_approved", "returns.ReturnRequest", return_request.id, actor=actor)
        return return_request

    @staticmethod
    @transaction.atomic
    def receive(return_item, warehouse, actor=None):
        inv, _ = WarehouseInventory.objects.select_for_update().get_or_create(
            product=return_item.order_item.product,
            variant=return_item.order_item.variant,
            warehouse=warehouse,
            defaults={"physical_stock": 0},
        )
        previous = inv.returned_stock
        inv.returned_stock += return_item.quantity
        if return_item.restock_decision == "restock":
            inv.physical_stock += return_item.quantity
        inv.save(update_fields=["returned_stock", "physical_stock"])
        InventoryTransaction.objects.create(
            inventory=inv,
            transaction_type=InventoryTransaction.Type.RETURN,
            previous_quantity=previous,
            quantity_change=return_item.quantity,
            new_quantity=inv.returned_stock,
            reason="Return received",
            reference_type="return_item",
            reference_id=str(return_item.id),
            actor=actor,
        )
        AuditService.log("return_received", "returns.ReturnItem", return_item.id, actor=actor)
        return inv
