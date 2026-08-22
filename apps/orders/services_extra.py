from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.crypto import get_random_string
from apps.analytics.audit import AuditService
from apps.inventory.services import InventoryService
from .models import CancellationRequest, Invoice, Order, OrderStatusHistory


class OrderStateService:
    ALLOWED = {
        Order.Status.PENDING: {Order.Status.CONFIRMED, Order.Status.CANCELLED},
        Order.Status.CONFIRMED: {Order.Status.PACKED, Order.Status.CANCELLED},
        Order.Status.PACKED: {Order.Status.SHIPPED, Order.Status.CANCELLED},
        Order.Status.SHIPPED: {Order.Status.DELIVERED, Order.Status.RETURNED},
        Order.Status.DELIVERED: {Order.Status.RETURNED},
    }

    @staticmethod
    @transaction.atomic
    def transition(order, new_status, actor=None, note=""):
        if new_status not in OrderStateService.ALLOWED.get(order.status, set()):
            raise ValidationError(f"Cannot move order from {order.status} to {new_status}.")
        previous = order.status
        order.status = new_status
        order.save(update_fields=["status"])
        OrderStatusHistory.objects.create(order=order, previous_status=previous, new_status=new_status, changed_by=actor, note=note)
        return order


class InvoiceService:
    @staticmethod
    def create_for_order(order):
        invoice, _ = Invoice.objects.get_or_create(
            order=order,
            defaults={
                "invoice_number": f"INV{get_random_string(10).upper()}",
                "billing_snapshot": {"address_id": order.shipping_address_id},
                "shipping_snapshot": {"address_id": order.shipping_address_id},
                "totals_snapshot": {
                    "subtotal": str(order.subtotal),
                    "coupon_discount": str(order.coupon_discount),
                    "tax": str(order.tax),
                    "shipping": str(order.shipping),
                    "grand_total": str(order.grand_total),
                },
            },
        )
        return invoice


class CancellationService:
    @staticmethod
    @transaction.atomic
    def approve(cancellation, actor=None):
        if cancellation.status != "requested":
            return cancellation
        order = cancellation.order
        previous = order.status
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        cancellation.status = "approved"
        cancellation.save(update_fields=["status"])
        for item in order.items.select_related("product", "variant"):
            InventoryService.release(item.product, item.variant, item.quantity, "cancellation", str(cancellation.id), actor)
        OrderStatusHistory.objects.create(order=order, previous_status=previous, new_status=order.status, changed_by=actor, note="Cancellation approved")
        AuditService.log("cancellation_approved", "orders.CancellationRequest", cancellation.id, actor=actor, previous={"order_status": previous}, new={"order_status": order.status})
        return cancellation

    @staticmethod
    def reject(cancellation, actor=None, note=""):
        cancellation.status = "rejected"
        cancellation.save(update_fields=["status"])
        AuditService.log("cancellation_rejected", "orders.CancellationRequest", cancellation.id, actor=actor, new={"note": note})
        return cancellation
