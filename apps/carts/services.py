from django.db import transaction
from .models import Cart, CartItem


class CartService:
    SESSION_KEY = "guest_cart"

    @staticmethod
    def get_or_create_for_request(request):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
        return cart

    @staticmethod
    @transaction.atomic
    def merge_guest_cart(request, user):
        session_key = request.session.session_key
        if not session_key:
            return Cart.objects.get_or_create(user=user)[0]
        guest = Cart.objects.filter(session_key=session_key, user=None).first()
        customer, _ = Cart.objects.get_or_create(user=user)
        if not guest:
            return customer
        for item in guest.items.select_related("product", "variant"):
            target, created = CartItem.objects.get_or_create(
                cart=customer,
                product=item.product,
                variant=item.variant,
                defaults={"quantity": item.quantity},
            )
            if not created:
                target.quantity += item.quantity
                target.save(update_fields=["quantity"])
        guest.delete()
        return customer
