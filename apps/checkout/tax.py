from decimal import Decimal


class TaxService:
    DEFAULT_GST_RATE = Decimal("0.18")

    @staticmethod
    def calculate(subtotal_after_discount, rate=None):
        return subtotal_after_discount * (rate or TaxService.DEFAULT_GST_RATE)
