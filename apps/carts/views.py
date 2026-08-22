from decimal import Decimal
from django.views.generic import TemplateView
from apps.carts.models import Cart
from .services import CartService
from apps.checkout.services import CheckoutService


class CartPageView(TemplateView):
    template_name = "cart/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart = CartService.get_or_create_for_request(self.request)
        elif self.request.session.session_key:
            cart = Cart.objects.filter(session_key=self.request.session.session_key, user=None).first()
        else:
            cart = None
        context["cart"] = cart
        context["summary"] = CheckoutService.summarize(cart) if cart else {
            "lines": [],
            "mrp_total": Decimal("0.00"),
            "subtotal": Decimal("0.00"),
            "coupon_discount": Decimal("0.00"),
            "tax": Decimal("0.00"),
            "shipping": Decimal("0.00"),
            "final_total": Decimal("0.00"),
        }
        return context
