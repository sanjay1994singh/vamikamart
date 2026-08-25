from decimal import Decimal
import pytest
from apps.accounts.models import User
from apps.carts.models import Cart, CartItem
from apps.catalog.models import Category, Product
from apps.shipping.rates import ShippingRateService
from apps.checkout.tax import TaxService
from apps.checkout.services import CheckoutService


def test_shipping_free_threshold():
    assert ShippingRateService.calculate(Decimal("999.00")) == Decimal("0.00")
    assert ShippingRateService.calculate(Decimal("100.00")) == Decimal("79.00")


def test_tax_service_uses_decimal_rate():
    assert TaxService.calculate(Decimal("100.00")) == Decimal("18.0000")


@pytest.mark.django_db
def test_empty_cart_summary_has_zero_shipping_and_total():
    user = User.objects.create_user(email="emptycart@example.com", password="pass12345")
    cart = Cart.objects.create(user=user)

    summary = CheckoutService.summarize(cart)

    assert summary["lines"] == []
    assert summary["subtotal"] == Decimal("0.00")
    assert summary["shipping"] == Decimal("0.00")
    assert summary["final_total"] == Decimal("0.00")


@pytest.mark.django_db
def test_non_empty_cart_summary_uses_real_backend_totals():
    user = User.objects.create_user(email="pricedcart@example.com", password="pass12345")
    category = Category.objects.create(name="Grocery", slug="grocery")
    product = Product.objects.create(
        name="Rice",
        slug="rice",
        sku="RICE-SUMMARY",
        category=category,
        mrp="70.00",
        selling_price="50.00",
        status=Product.Status.ACTIVE,
    )
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)

    summary = CheckoutService.summarize(cart)

    assert summary["subtotal"] == Decimal("100.00")
    assert summary["tax"] == Decimal("18.0000")
    assert summary["shipping"] == Decimal("79.00")
    assert summary["final_total"] == Decimal("197.0000")
