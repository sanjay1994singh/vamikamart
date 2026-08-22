from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.analytics.audit import AuditService
from .models import Refund


class RefundCalculationService:
    @staticmethod
    def calculate(order, items=None, shipping_refundable=False):
        if not items:
            base = order.grand_total
        else:
            base = sum((item.line_total for item in items), Decimal("0.00"))
        if shipping_refundable:
            base += order.shipping
        return max(base, Decimal("0.00"))


class RefundService:
    @staticmethod
    @transaction.atomic
    def create_for_order(order, amount=None, payment=None):
        refund = Refund.objects.create(
            order=order,
            payment=payment or getattr(order, "payment", None),
            amount=amount if amount is not None else RefundCalculationService.calculate(order),
            status="pending",
        )
        AuditService.log("refund_created", "refunds.Refund", refund.id, new={"amount": str(refund.amount)})
        return refund

    @staticmethod
    def mark_completed(refund, provider_refund_id=""):
        refund.status = "completed"
        refund.provider_refund_id = provider_refund_id
        refund.save(update_fields=["status", "provider_refund_id"])
        if hasattr(refund, "reconciliation"):
            refund.reconciliation.reconciled = True
            refund.reconciliation.reconciled_at = timezone.now()
            refund.reconciliation.save(update_fields=["reconciled", "reconciled_at"])
        AuditService.log("refund_completed", "refunds.Refund", refund.id)
        return refund
