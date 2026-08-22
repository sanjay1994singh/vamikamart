from django.contrib import admin
from .models import CancellationRequest, CreditNote, Invoice, Order, OrderInternalNote, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "sku", "quantity", "unit_price", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "user", "status", "grand_total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "user__email")
    readonly_fields = ("created_at",)
    inlines = [OrderItemInline]


admin.site.register(OrderStatusHistory)
admin.site.register(OrderInternalNote)
admin.site.register(CancellationRequest)
admin.site.register(Invoice)
admin.site.register(CreditNote)
