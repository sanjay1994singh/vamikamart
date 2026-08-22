from decimal import Decimal
from apps.shipping.rates import ShippingRateService
from apps.checkout.tax import TaxService


def test_shipping_free_threshold():
    assert ShippingRateService.calculate(Decimal("999.00")) == Decimal("0.00")
    assert ShippingRateService.calculate(Decimal("100.00")) == Decimal("79.00")


def test_tax_service_uses_decimal_rate():
    assert TaxService.calculate(Decimal("100.00")) == Decimal("18.0000")
