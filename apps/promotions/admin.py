from django.contrib import admin
from .models import Coupon, CouponRedemption, FlashSale, FlashSaleItem


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "minimum_order", "active", "start_date", "expiry_date")
    list_filter = ("discount_type", "active", "first_order_only")
    search_fields = ("code",)


admin.site.register(CouponRedemption)
admin.site.register(FlashSale)
admin.site.register(FlashSaleItem)
