from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import Brand, Category, Product
from apps.catalog.views import DUMMY_PRODUCTS
from apps.inventory.models import Warehouse, WarehouseInventory


class Command(BaseCommand):
    help = "Seed VamikaMart dummy grocery products used by the storefront fallback."

    def handle(self, *args, **options):
        warehouse, _ = Warehouse.objects.get_or_create(
            code="VM-DUMMY",
            defaults={"name": "VamikaMart Demo Warehouse", "city": "Varanasi", "state": "Uttar Pradesh"},
        )
        category, _ = Category.objects.get_or_create(
            slug="vm-dummy-grocery",
            defaults={"name": "VamikaMart Demo Grocery", "featured": False, "active": True},
        )
        brand, _ = Brand.objects.get_or_create(
            slug="vamikamart-demo",
            defaults={"name": "VamikaMart Demo", "featured": False, "active": True},
        )
        for item in DUMMY_PRODUCTS:
            product, _ = Product.objects.update_or_create(
                sku=item["sku"],
                defaults={
                    "name": item["name"],
                    "slug": slugify(item["name"]),
                    "category": category,
                    "brand": brand,
                    "short_description": f"{item['size']} daily grocery item for storefront preview.",
                    "mrp": Decimal(str(item["mrp"])),
                    "selling_price": Decimal(str(item["price"])),
                    "cost_price": Decimal("0.00"),
                    "featured": False,
                    "status": Product.Status.ACTIVE,
                },
            )
            WarehouseInventory.objects.update_or_create(
                product=product,
                variant=None,
                warehouse=warehouse,
                defaults={"physical_stock": 500, "reserved_stock": 0, "damaged_stock": 0},
            )
        self.stdout.write(self.style.SUCCESS("VamikaMart dummy storefront products seeded."))
