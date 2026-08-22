from django.contrib import admin
from .models import NDRRecord, RTORecord, Shipment, ShippingManifest


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("order", "carrier", "awb", "status", "shipped_at", "delivered_at")
    list_filter = ("status", "carrier")
    search_fields = ("order__order_number", "awb", "carrier")


admin.site.register(ShippingManifest)
admin.site.register(NDRRecord)
admin.site.register(RTORecord)
