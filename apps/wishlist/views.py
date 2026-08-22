from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import WishlistItem


class WishlistPageView(LoginRequiredMixin, ListView):
    template_name = "wishlist/index.html"

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related("product", "variant").order_by("-created_at")
