from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.shortcuts import render
from apps.analytics.models import ActionQueueItem, OperationalExpense
from apps.catalog.models import Product
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.accounts.models import User


@staff_member_required
def owner_dashboard(request):
    orders = Order.objects.all()
    payments = Payment.objects.all()
    context = {
        "order_count": orders.count(),
        "revenue": orders.aggregate(total=Sum("grand_total"))["total"] or 0,
        "paid_total": payments.filter(status=Payment.Status.PAID).aggregate(total=Sum("amount"))["total"] or 0,
        "pending_orders": orders.filter(status=Order.Status.PENDING).count(),
    }
    return render(request, "analytics/dashboard.html", context)


@staff_member_required
def reports(request):
    revenue = Order.objects.aggregate(total=Sum("grand_total"))["total"] or 0
    expenses = OperationalExpense.objects.aggregate(total=Sum("amount"))["total"] or 0
    return render(request, "analytics/reports.html", {"revenue": revenue, "expenses": expenses, "profit": revenue - expenses})


@staff_member_required
def action_queues(request):
    items = ActionQueueItem.objects.filter(resolved_at__isnull=True).order_by("-priority", "-created_at")
    return render(request, "analytics/action_queues.html", {"items": items})


@staff_member_required
def owner_search(request):
    query = request.GET.get("q", "")
    context = {"query": query, "products": [], "orders": [], "customers": []}
    if query:
        context["products"] = Product.objects.filter(Q(name__icontains=query) | Q(sku__icontains=query))[:10]
        context["orders"] = Order.objects.filter(order_number__icontains=query)[:10]
        context["customers"] = User.objects.filter(Q(email__icontains=query) | Q(mobile_number__icontains=query))[:10]
    return render(request, "analytics/search.html", context)


@staff_member_required
def order_filters(request):
    orders = Order.objects.all().order_by("-created_at")
    status = request.GET.get("status")
    if status:
        orders = orders.filter(status=status)
    return render(request, "analytics/order_filters.html", {"orders": orders[:100], "status": status})
