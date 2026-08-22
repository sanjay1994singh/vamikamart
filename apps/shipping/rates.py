from decimal import Decimal


class ShippingRateService:
    FREE_SHIPPING_THRESHOLD = Decimal("999.00")
    STANDARD_RATE = Decimal("79.00")

    @staticmethod
    def calculate(subtotal):
        return Decimal("0.00") if subtotal >= ShippingRateService.FREE_SHIPPING_THRESHOLD else ShippingRateService.STANDARD_RATE

    @staticmethod
    def is_pin_serviceable(pin_code):
        return bool(pin_code and len(str(pin_code)) >= 5)
