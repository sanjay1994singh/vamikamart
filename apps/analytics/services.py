from django.db.models import Sum
from apps.orders.models import Order
from apps.support.models import SupportTicket
from .models import ActionQueueItem, CustomerMetricSnapshot


class CustomerMetricsService:
    @staticmethod
    def refresh(user):
        orders = Order.objects.filter(user=user)
        snapshot, _ = CustomerMetricSnapshot.objects.update_or_create(
            user=user,
            defaults={
                "order_count": orders.count(),
                "lifetime_value": orders.aggregate(total=Sum("grand_total"))["total"] or 0,
                "last_order_at": orders.order_by("-created_at").values_list("created_at", flat=True).first(),
                "support_ticket_count": SupportTicket.objects.filter(user=user).count(),
            },
        )
        return snapshot


class ActionQueueService:
    @staticmethod
    def create(queue, title, entity="", object_id="", priority=ActionQueueItem.Priority.NORMAL):
        return ActionQueueItem.objects.create(queue=queue, title=title, entity=entity, object_id=object_id, priority=priority)
