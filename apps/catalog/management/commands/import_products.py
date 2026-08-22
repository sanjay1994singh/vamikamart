import csv
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = "Import or update simple products from CSV."

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        created = updated = 0
        try:
            handle = open(options["path"], newline="", encoding="utf-8")
        except OSError as exc:
            raise CommandError(str(exc))
        with handle:
            for row in csv.DictReader(handle):
                category, _ = Category.objects.get_or_create(
                    slug=slugify(row["category"]),
                    defaults={"name": row["category"]},
                )
                _, was_created = Product.objects.update_or_create(
                    sku=row["sku"],
                    defaults={
                        "name": row["name"],
                        "slug": row.get("slug") or slugify(row["name"]),
                        "category": category,
                        "mrp": Decimal(row["mrp"]),
                        "selling_price": Decimal(row["selling_price"]),
                        "status": row.get("status") or Product.Status.DRAFT,
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created}, updated {updated} products."))
