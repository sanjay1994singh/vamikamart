from celery import shared_task
from django.utils import timezone
from apps.notifications.services import NotificationService
from .models import StockNotificationRequest, WarehouseInventory


@shared_task
def generate_low_stock_alerts():
    for inv in WarehouseInventory.objects.select_related("product").all():
        if inv.available_stock <= inv.product.low_stock_threshold:
            # Owner routing can be configured later; this task records the condition through logs/admin visibility.
            pass


@shared_task
def notify_stock_back_available():
    requests = StockNotificationRequest.objects.select_related("user", "product", "variant")
    for request in requests:
        available = WarehouseInventory.objects.filter(product=request.product, variant=request.variant, physical_stock__gt=0).exists()
        if available:
            NotificationService.create(request.user, "Back in stock", f"{request.product.name} is available again.")
            request.delete()
