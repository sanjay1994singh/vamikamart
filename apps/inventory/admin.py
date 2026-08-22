from django.contrib import admin
from .models import InventoryTransaction, StockNotificationRequest, Warehouse, WarehouseInventory


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "state", "active")
    list_filter = ("active", "state")
    search_fields = ("name", "code", "city")


@admin.register(WarehouseInventory)
class WarehouseInventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "variant", "warehouse", "physical_stock", "reserved_stock", "available_stock", "damaged_stock")
    list_filter = ("warehouse",)
    search_fields = ("product__name", "product__sku", "variant__sku")


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ("inventory", "transaction_type", "quantity_change", "new_quantity", "reference_type", "reference_id", "created_at")
    list_filter = ("transaction_type", "created_at")
    search_fields = ("inventory__product__name", "reference_type", "reference_id")
    readonly_fields = ("created_at",)


admin.site.register(StockNotificationRequest)
