from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("purchase_number", "supplier", "warehouse", "purchase_date", "status", "grand_total")
    list_filter = ("status", "purchase_date", "warehouse")
    search_fields = ("purchase_number", "supplier__supplier_name")
    inlines = [PurchaseOrderItemInline]
