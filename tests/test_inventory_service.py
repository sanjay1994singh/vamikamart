import pytest
from django.core.exceptions import ValidationError
from apps.catalog.models import Category, Product
from apps.inventory.models import Warehouse, WarehouseInventory
from apps.inventory.services import InventoryService


@pytest.mark.django_db
def test_reserve_rejects_oversell():
    category = Category.objects.create(name="Phones", slug="phones")
    product = Product.objects.create(name="Phone", slug="phone", sku="P1", category=category, mrp=100, selling_price=90, status=Product.Status.ACTIVE)
    warehouse = Warehouse.objects.create(name="Main", code="MAIN")
    WarehouseInventory.objects.create(product=product, warehouse=warehouse, physical_stock=1)

    InventoryService.reserve(product, None, 1)

    with pytest.raises(ValidationError):
        InventoryService.reserve(product, None, 1)
