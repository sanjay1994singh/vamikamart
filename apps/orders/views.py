from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView
from .models import Order
from .services_extra import InvoiceService


class OrderListPageView(LoginRequiredMixin, ListView):
    template_name = "orders/index.html"
    paginate_by = 20

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class OrderDetailPageView(LoginRequiredMixin, DetailView):
    template_name = "orders/detail.html"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


@staff_member_required
def invoice_view(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
    invoice = InvoiceService.create_for_order(order)
    return render(request, "orders/invoice.html", {"order": order, "invoice": invoice})
