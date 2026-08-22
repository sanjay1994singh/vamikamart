from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from apps.carts.services import CartService
from .services import CheckoutService


class CheckoutPageView(LoginRequiredMixin, TemplateView):
    template_name = "checkout/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartService.get_or_create_for_request(self.request)
        context["cart"] = cart
        context["summary"] = CheckoutService.summarize(cart)
        context["addresses"] = self.request.user.addresses.all()
        return context
