import csv
from django.core.management.base import BaseCommand
from apps.orders.models import Order


class Command(BaseCommand):
    help = "Export orders to CSV."

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        with open(options["path"], "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["order_number", "customer", "status", "subtotal", "tax", "shipping", "grand_total", "created_at"])
            for order in Order.objects.select_related("user").order_by("-created_at"):
                writer.writerow([order.order_number, order.user.email, order.status, order.subtotal, order.tax, order.shipping, order.grand_total, order.created_at])
        self.stdout.write(self.style.SUCCESS(f"Exported orders to {options['path']}"))
