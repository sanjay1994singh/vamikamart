import pytest
from datetime import date
from apps.accounts.models import Address, User
from apps.catalog.models import Category, Product
from apps.inventory.models import Warehouse, WarehouseInventory
from apps.orders.models import Order
from apps.purchases.models import PurchaseOrder, PurchaseOrderItem
from apps.purchases.services import PurchaseService
from apps.suppliers.models import Supplier


@pytest.mark.django_db
def test_business_owner_purchase_inventory_publish_customer_order(api_client):
    owner = User.objects.create_user(email="owner2@example.com", username="owner2", password="pass12345", role=User.Role.OWNER, is_staff=True)
    customer = User.objects.create_user(email="customer@example.com", username="customer", password="pass12345")
    supplier = Supplier.objects.create(supplier_name="Main Supplier", phone="999")
    warehouse = Warehouse.objects.create(name="Main Warehouse", code="MW")
    category = Category.objects.create(name="Mobiles", slug="mobiles")
    product = Product.objects.create(name="Demo Mobile", slug="demo-mobile", sku="DM-1", category=category, mrp="12000.00", selling_price="10000.00", status=Product.Status.DRAFT)
    po = PurchaseOrder.objects.create(purchase_number="PO-1", supplier=supplier, warehouse=warehouse, purchase_date=date.today(), status=PurchaseOrder.Status.ORDERED)
    item = PurchaseOrderItem.objects.create(
        purchase_order=po,
        product=product,
        sku=product.sku,
        quantity_ordered=10,
        purchase_cost="7000.00",
        total="70000.00",
    )

    PurchaseService.receive_item(item, received_qty=10, actor=owner)
    product.status = Product.Status.ACTIVE
    product.save()

    inventory = WarehouseInventory.objects.get(product=product, warehouse=warehouse)
    assert inventory.physical_stock == 10
    assert PurchaseOrder.objects.get(id=po.id).status == PurchaseOrder.Status.RECEIVED

    address = Address.objects.create(user=customer, full_name="Customer", phone="999", house="1", street="Main", locality="Central", city="Delhi", state="Delhi", pin_code="110001")
    api_client.force_authenticate(customer)
    api_client.post("/api/v1/cart/add/", {"product_id": product.id, "quantity": 1}, format="json")
    response = api_client.post("/api/v1/cart/place_order/", {"address_id": address.id, "payment_method": "cod"}, format="json", HTTP_IDEMPOTENCY_KEY="owner-journey")

    assert response.status_code == 200
    assert Order.objects.filter(user=customer).count() == 1
