from django.contrib import admin
from .models import CODSettlement, Payment, PaymentReconciliation, WebhookEventLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "method", "status", "amount", "provider_payment_id", "created_at")
    list_filter = ("method", "status", "created_at")
    search_fields = ("order__order_number", "provider_order_id", "provider_payment_id")


@admin.register(WebhookEventLog)
class WebhookEventLogAdmin(admin.ModelAdmin):
    list_display = ("provider", "event_id", "event_type", "processing_status", "received_at")
    list_filter = ("provider", "processing_status", "received_at")
    search_fields = ("event_id", "event_type")


admin.site.register(CODSettlement)
admin.site.register(PaymentReconciliation)
