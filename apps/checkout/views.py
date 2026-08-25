from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from apps.accounts.forms import AddressForm
from apps.carts.services import CartService
from .services import CheckoutService


class CheckoutPageView(LoginRequiredMixin, TemplateView):
    template_name = "checkout/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartService.get_or_create_for_request(self.request)
        context["cart"] = cart
        context["summary"] = CheckoutService.summarize(cart)
        context["addresses"] = self.request.user.addresses.order_by("-default_shipping", "-created_at")
        context["selected_address_id"] = self.request.GET.get("address_id")
        context["address_form"] = AddressForm(initial={
            "full_name": self.request.user.get_full_name() or self.request.user.email,
            "phone": self.request.user.mobile_number,
            "country": "India",
            "default_shipping": not self.request.user.addresses.exists(),
            "default_billing": not self.request.user.addresses.exists(),
        })
        return context
