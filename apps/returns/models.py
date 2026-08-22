from django.conf import settings
from django.db import models


class ReturnRequest(models.Model):
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="returns")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.TextField()
    status = models.CharField(max_length=40, default="requested")
    created_at = models.DateTimeField(auto_now_add=True)


class ReturnItem(models.Model):
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey("orders.OrderItem", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=40, default="uninspected")
    restock_decision = models.CharField(max_length=40, default="pending")
