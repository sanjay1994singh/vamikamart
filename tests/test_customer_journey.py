import pytest
from decimal import Decimal
from apps.accounts.models import Address, User
from apps.catalog.models import Category, Product
from apps.inventory.models import Warehouse, WarehouseInventory
from apps.orders.models import Order
from apps.orders.models import CancellationRequest
from apps.payments.models import CODSettlement, Payment


@pytest.mark.django_db
def test_customer_cart_checkout_order_journey(api_client):
    user = User.objects.create_user(email="buyer@example.com", username="buyer", password="pass12345")
    category = Category.objects.create(name="Electronics", slug="electronics")
    product = Product.objects.create(
        name="Phone",
        slug="phone",
        sku="PHONE-1",
        category=category,
        mrp="10000.00",
        selling_price="9000.00",
        status=Product.Status.ACTIVE,
    )
    warehouse = Warehouse.objects.create(name="Main", code="MAIN")
    WarehouseInventory.objects.create(product=product, warehouse=warehouse, physical_stock=5)
    address = Address.objects.create(
        user=user,
        full_name="Buyer",
        phone="9999999999",
        house="1",
        street="Market Road",
        locality="Central",
        city="Delhi",
        state="Delhi",
        pin_code="110001",
    )

    api_client.force_authenticate(user)
    add_response = api_client.post("/api/v1/cart/add/", {"product_id": product.id, "quantity": 2}, format="json")
    assert add_response.status_code == 200

    quote_response = api_client.post("/api/v1/cart/quote/", {}, format="json")
    assert quote_response.status_code == 200
    assert quote_response.data["data"]["subtotal"] == Decimal("18000.00")

    order_response = api_client.post(
        "/api/v1/cart/place_order/",
        {"address_id": address.id, "payment_method": "cod"},
        format="json",
        HTTP_IDEMPOTENCY_KEY="journey-1",
    )
    assert order_response.status_code == 200
    assert Order.objects.filter(user=user).count() == 1
    assert Payment.objects.filter(order__user=user, method=Payment.Method.COD).count() == 1
    assert CODSettlement.objects.filter(order__user=user, status="pending").count() == 1
    order = Order.objects.get(user=user)

    web_client = api_client
    web_client.force_login(user)
    orders_page = web_client.get("/orders/")
    assert orders_page.status_code == 200
    content = orders_page.content.decode()
    assert f'href="/orders/{order.id}/"' in content
    assert f"/api/v1/orders/{order.id}/" not in content

    repeat_response = api_client.post(
        "/api/v1/cart/place_order/",
        {"address_id": address.id, "payment_method": "cod"},
        format="json",
        HTTP_IDEMPOTENCY_KEY="journey-1",
    )
    assert repeat_response.status_code == 200
    assert Order.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_customer_can_cancel_order_and_record_is_kept(api_client):
    user = User.objects.create_user(email="cancel@example.com", username="cancel", password="pass12345")
    category = Category.objects.create(name="Grocery", slug="grocery")
    product = Product.objects.create(
        name="Banana",
        slug="banana-cancel",
        sku="BANANA-CANCEL",
        category=category,
        mrp="50.00",
        selling_price="42.00",
        status=Product.Status.ACTIVE,
    )
    warehouse = Warehouse.objects.create(name="Cancel Warehouse", code="CANCEL")
    inventory = WarehouseInventory.objects.create(product=product, warehouse=warehouse, physical_stock=10)
    address = Address.objects.create(
        user=user,
        full_name="Cancel User",
        phone="9999999999",
        house="1",
        street="Market Road",
        locality="Central",
        city="Delhi",
        state="Delhi",
        pin_code="110001",
    )

    api_client.force_authenticate(user)
    api_client.post("/api/v1/cart/add/", {"product_id": product.id, "quantity": 2}, format="json")
    order_response = api_client.post(
        "/api/v1/cart/place_order/",
        {"address_id": address.id, "payment_method": "cod"},
        format="json",
        HTTP_IDEMPOTENCY_KEY="cancel-journey",
    )
    order_id = order_response.data["data"]["id"]
    inventory.refresh_from_db()
    assert inventory.reserved_stock == 2

    cancel_response = api_client.post(
        f"/api/v1/orders/{order_id}/cancel/",
        {"reason": "Ordered by mistake"},
        format="json",
    )

    assert cancel_response.status_code == 200
    order = Order.objects.get(id=order_id)
    inventory.refresh_from_db()
    cancellation = CancellationRequest.objects.get(order=order)
    assert order.status == Order.Status.CANCELLED
    assert cancellation.reason == "Ordered by mistake"
    assert cancellation.status == "approved"
    assert inventory.reserved_stock == 0
    assert order.status_history.filter(new_status=Order.Status.CANCELLED, note="Cancelled by customer").exists()
