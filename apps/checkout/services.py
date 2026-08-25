from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.promotions.models import Coupon
from apps.promotions.models import CouponRedemption
from apps.orders.models import Order
from .tax import TaxService
from apps.shipping.rates import ShippingRateService


class PricingService:
    @staticmethod
    def unit_price(item):
        if item.variant and item.variant.selling_price:
            return item.variant.selling_price
        return item.product.selling_price


class CouponService:
    @staticmethod
    def calculate_discount(coupon, subtotal):
        if not coupon:
            return Decimal("0.00")
        now = timezone.now()
        if not coupon.active or coupon.start_date > now or coupon.expiry_date < now:
            raise ValidationError("Coupon is not valid.")
        if subtotal < coupon.minimum_order:
            raise ValidationError("Minimum order value not met.")
        if coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
            discount = subtotal * coupon.discount_value / Decimal("100")
        else:
            discount = coupon.discount_value
        if coupon.maximum_discount:
            discount = min(discount, coupon.maximum_discount)
        return min(discount, subtotal)

    @staticmethod
    def validate_for_customer(coupon, user, subtotal):
        discount = CouponService.calculate_discount(coupon, subtotal)
        if coupon.total_usage_limit and CouponRedemption.objects.filter(coupon=coupon).count() >= coupon.total_usage_limit:
            raise ValidationError("Coupon usage limit reached.")
        if user and user.is_authenticated:
            used = CouponRedemption.objects.filter(coupon=coupon, user=user).count()
            if used >= coupon.per_customer_limit:
                raise ValidationError("Coupon usage limit reached for this customer.")
            if coupon.first_order_only and Order.objects.filter(user=user).exists():
                raise ValidationError("Coupon is only valid on first order.")
        return discount


class CheckoutService:
    @staticmethod
    def summarize(cart):
        subtotal = Decimal("0.00")
        mrp_total = Decimal("0.00")
        lines = []
        for item in cart.items.select_related("product", "variant").filter(saved_for_later=False):
            unit = PricingService.unit_price(item)
            mrp = item.variant.mrp or item.product.mrp if item.variant else item.product.mrp
            line_total = unit * item.quantity
            subtotal += line_total
            mrp_total += mrp * item.quantity
            lines.append({"item": item, "unit_price": unit, "line_total": line_total})
        if not lines:
            return {
                "lines": [],
                "mrp_total": Decimal("0.00"),
                "subtotal": Decimal("0.00"),
                "coupon_discount": Decimal("0.00"),
                "tax": Decimal("0.00"),
                "shipping": Decimal("0.00"),
                "final_total": Decimal("0.00"),
            }
        coupon_discount = CouponService.validate_for_customer(cart.coupon, cart.user, subtotal) if cart.coupon else Decimal("0.00")
        tax = TaxService.calculate(subtotal - coupon_discount)
        shipping = ShippingRateService.calculate(subtotal)
        final_total = subtotal - coupon_discount + tax + shipping
        return {
            "lines": lines,
            "mrp_total": mrp_total,
            "subtotal": subtotal,
            "coupon_discount": coupon_discount,
            "tax": tax,
            "shipping": shipping,
            "final_total": final_total,
        }


class DiscountAllocationService:
    @staticmethod
    def allocate_discount(lines, discount_total):
        subtotal = sum((line["line_total"] for line in lines), Decimal("0.00"))
        if subtotal <= 0 or discount_total <= 0:
            return {line["item"].id: Decimal("0.00") for line in lines}
        allocated = {}
        running = Decimal("0.00")
        for line in lines[:-1]:
            amount = (line["line_total"] / subtotal * discount_total).quantize(Decimal("0.01"))
            allocated[line["item"].id] = amount
            running += amount
        if lines:
            allocated[lines[-1]["item"].id] = discount_total - running
        return allocated
