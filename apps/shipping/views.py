from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from apps.orders.models import Order
from .models import ShippingManifest


@staff_member_required
def packing_slip(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related("items"), id=order_id)
    return render(request, "shipping/packing_slip.html", {"order": order})


@staff_member_required
def shipping_label(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "shipping/shipping_label.html", {"order": order})


@staff_member_required
def manifest_view(request, manifest_id):
    manifest = get_object_or_404(ShippingManifest.objects.prefetch_related("shipments__order"), id=manifest_id)
    return render(request, "shipping/manifest.html", {"manifest": manifest})
