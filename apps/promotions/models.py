from django.conf import settings
from django.db import models


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FLAT = "flat", "Flat"

    code = models.CharField(max_length=40, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    maximum_discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    minimum_order = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateTimeField()
    expiry_date = models.DateTimeField()
    total_usage_limit = models.PositiveIntegerField(null=True, blank=True)
    per_customer_limit = models.PositiveIntegerField(default=1)
    applicable_products = models.ManyToManyField("catalog.Product", blank=True, related_name="coupons")
    applicable_categories = models.ManyToManyField("catalog.Category", blank=True, related_name="coupons")
    excluded_products = models.ManyToManyField("catalog.Product", blank=True, related_name="excluded_coupons")
    first_order_only = models.BooleanField(default=False)
    active = models.BooleanField(default=True)


class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    order = models.ForeignKey("orders.Order", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class FlashSale(models.Model):
    name = models.CharField(max_length=160)
    products = models.ManyToManyField("catalog.Product", through="FlashSaleItem", related_name="flash_sales")
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    active = models.BooleanField(default=True)


class FlashSaleItem(models.Model):
    flash_sale = models.ForeignKey(FlashSale, on_delete=models.CASCADE)
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE)
    variant = models.ForeignKey("catalog.ProductVariant", null=True, blank=True, on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_limit = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("flash_sale", "product", "variant")
