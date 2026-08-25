import pytest
import hmac
import hashlib
from decimal import Decimal
from django.test import override_settings
from apps.accounts.models import Address, User
from apps.catalog.models import Category, Product
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.services import PaymentService


@pytest.mark.django_db
def test_webhook_idempotency():
    first = PaymentService.process_webhook("test", "evt_1", "payment.captured", {"id": "evt_1"})
    second = PaymentService.process_webhook("test", "evt_1", "payment.captured", {"id": "evt_1"})
    assert first.id == second.id


@pytest.mark.django_db
@override_settings(RAZORPAY_KEY_SECRET="test_secret")
def test_confirm_razorpay_payment_marks_payment_paid():
    user = User.objects.create_user(email="pay@example.com", password="pass12345")
    category = Category.objects.create(name="Tea", slug="tea")
    product = Product.objects.create(
        name="Tea Pack",
        slug="tea-pack",
        sku="TEA-1",
        category=category,
        mrp="120.00",
        selling_price="100.00",
        status=Product.Status.ACTIVE,
    )
    address = Address.objects.create(user=user, full_name="Pay", phone="1", house="1", street="S", locality="L", city="C", state="S", pin_code="1")
    order = Order.objects.create(order_number="ORD-PAY", user=user, shipping_address=address, subtotal=100, tax=18, shipping=0, grand_total=118)
    payment = Payment.objects.create(order=order, method=Payment.Method.RAZORPAY, amount=Decimal("118.00"), provider_order_id="order_test")
    signature = hmac.new(b"test_secret", b"order_test|pay_test", hashlib.sha256).hexdigest()

    PaymentService.confirm_razorpay_payment(payment, "order_test", "pay_test", signature)

    payment.refresh_from_db()
    assert payment.status == Payment.Status.PAID
    assert payment.provider_payment_id == "pay_test"


@pytest.mark.django_db
@override_settings(RAZORPAY_KEY_SECRET="test_secret")
def test_confirm_razorpay_payment_rejects_bad_signature():
    user = User.objects.create_user(email="badpay@example.com", password="pass12345")
    category = Category.objects.create(name="Coffee", slug="coffee")
    product = Product.objects.create(
        name="Coffee Pack",
        slug="coffee-pack",
        sku="COFFEE-1",
        category=category,
        mrp="120.00",
        selling_price="100.00",
        status=Product.Status.ACTIVE,
    )
    address = Address.objects.create(user=user, full_name="Pay", phone="1", house="1", street="S", locality="L", city="C", state="S", pin_code="1")
    order = Order.objects.create(order_number="ORD-BADPAY", user=user, shipping_address=address, subtotal=100, tax=18, shipping=0, grand_total=118)
    payment = Payment.objects.create(order=order, method=Payment.Method.RAZORPAY, amount=Decimal("118.00"), provider_order_id="order_test")

    with pytest.raises(Exception):
        PaymentService.confirm_razorpay_payment(payment, "order_test", "pay_test", "bad")
