import csv
from django.core.management.base import BaseCommand
from apps.catalog.models import Product


class Command(BaseCommand):
    help = "Export products to CSV."

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        with open(options["path"], "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["sku", "name", "slug", "category", "brand", "mrp", "selling_price", "status"])
            for product in Product.objects.select_related("category", "brand").order_by("sku"):
                writer.writerow([
                    product.sku,
                    product.name,
                    product.slug,
                    product.category.name,
                    product.brand.name if product.brand else "",
                    product.mrp,
                    product.selling_price,
                    product.status,
                ])
        self.stdout.write(self.style.SUCCESS(f"Exported products to {options['path']}"))
