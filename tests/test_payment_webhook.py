import pytest
from apps.payments.services import PaymentService


@pytest.mark.django_db
def test_webhook_idempotency():
    first = PaymentService.process_webhook("test", "evt_1", "payment.captured", {"id": "evt_1"})
    second = PaymentService.process_webhook("test", "evt_1", "payment.captured", {"id": "evt_1"})
    assert first.id == second.id
