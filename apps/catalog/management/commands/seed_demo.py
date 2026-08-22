from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.accounts.models import User
from apps.catalog.models import Brand, Category, Product, ProductSpecification
from apps.inventory.models import Warehouse, WarehouseInventory


class Command(BaseCommand):
    help = "Seed realistic development data for the ecommerce backend."

    def handle(self, *args, **options):
        owner, _ = User.objects.get_or_create(
            email="owner@example.com",
            defaults={"username": "owner", "role": User.Role.OWNER, "is_staff": True, "is_superuser": True},
        )
        owner.set_password("Owner@12345")
        owner.save()

        warehouse, _ = Warehouse.objects.get_or_create(code="MAIN", defaults={"name": "Main Warehouse", "city": "Delhi", "state": "Delhi"})
        category, _ = Category.objects.get_or_create(name="Mobiles", slug="mobiles", defaults={"featured": True})
        brand, _ = Brand.objects.get_or_create(name="DemoTech", slug="demotech", defaults={"featured": True})
        products = [
            ("Demo Phone Pro", "DEMO-PHONE-PRO", Decimal("49999.00"), Decimal("42999.00"), 20),
            ("Demo Earbuds", "DEMO-EARBUDS", Decimal("2999.00"), Decimal("1999.00"), 3),
            ("Demo Power Bank", "DEMO-POWER", Decimal("1999.00"), Decimal("1499.00"), 0),
        ]
        for name, sku, mrp, price, stock in products:
            product, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "slug": slugify(name),
                    "category": category,
                    "brand": brand,
                    "mrp": mrp,
                    "selling_price": price,
                    "featured": True,
                    "status": Product.Status.ACTIVE if stock else Product.Status.OUT_OF_STOCK,
                    "short_description": "Demo product for local development.",
                },
            )
            ProductSpecification.objects.get_or_create(product=product, name="Warranty", defaults={"value": "1 year"})
            WarehouseInventory.objects.get_or_create(product=product, variant=None, warehouse=warehouse, defaults={"physical_stock": stock})
        self.stdout.write(self.style.SUCCESS("Demo data created. Owner login: owner@example.com / Owner@12345"))
