from django.db import transaction
from django.utils.crypto import get_random_string
from apps.checkout.services import CheckoutService
from apps.inventory.services import InventoryService
from .models import Order, OrderItem


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_from_cart(cart, address, user):
        summary = CheckoutService.summarize(cart)
        order = Order.objects.create(
            order_number=f"ORD{get_random_string(10).upper()}",
            user=user,
            shipping_address=address,
            subtotal=summary["subtotal"],
            coupon_discount=summary["coupon_discount"],
            tax=summary["tax"],
            shipping=summary["shipping"],
            grand_total=summary["final_total"],
        )
        for line in summary["lines"]:
            item = line["item"]
            InventoryService.reserve(item.product, item.variant, item.quantity, "order", str(order.id), user)
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                sku=item.variant.sku if item.variant else item.product.sku,
                quantity=item.quantity,
                unit_price=line["unit_price"],
                line_total=line["line_total"],
            )
        return order
