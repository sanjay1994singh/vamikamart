import pytest
from apps.accounts.models import Address, User
from apps.carts.models import Cart
from apps.orders.models import Order


@pytest.mark.django_db
def test_customer_address_queryset_is_isolated(api_client):
    first = User.objects.create_user(email="a@example.com", username="a", password="pass12345")
    second = User.objects.create_user(email="b@example.com", username="b", password="pass12345")
    Address.objects.create(user=second, full_name="B", phone="1", house="1", street="S", locality="L", city="C", state="S", pin_code="1")

    api_client.force_authenticate(first)
    response = api_client.get("/api/v1/addresses/")

    assert response.status_code == 200
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_customer_cart_queryset_is_isolated(api_client):
    first = User.objects.create_user(email="a@example.com", username="a", password="pass12345")
    second = User.objects.create_user(email="b@example.com", username="b", password="pass12345")
    Cart.objects.create(user=second)

    api_client.force_authenticate(first)
    response = api_client.get("/api/v1/cart/")

    assert response.status_code == 200
    assert response.data["count"] == 0
