import csv
from django.core.management.base import BaseCommand
from apps.inventory.models import WarehouseInventory


class Command(BaseCommand):
    help = "Export inventory to CSV."

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        with open(options["path"], "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["warehouse", "product", "variant", "physical_stock", "reserved_stock", "available_stock", "damaged_stock"])
            for inv in WarehouseInventory.objects.select_related("warehouse", "product", "variant"):
                writer.writerow([inv.warehouse.code, inv.product.sku, inv.variant.sku if inv.variant else "", inv.physical_stock, inv.reserved_stock, inv.available_stock, inv.damaged_stock])
        self.stdout.write(self.style.SUCCESS(f"Exported inventory to {options['path']}"))
