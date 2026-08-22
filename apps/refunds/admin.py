from django.contrib import admin
from .models import Refund, RefundReconciliation


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("order", "payment", "amount", "status", "provider_refund_id", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__order_number", "provider_refund_id")


admin.site.register(RefundReconciliation)
