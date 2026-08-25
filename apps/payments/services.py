import hmac
import hashlib
import json
import base64
import urllib.request
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import CODSettlement, Payment, PaymentReconciliation, WebhookEventLog


class PaymentService:
    @staticmethod
    def create_razorpay_order(payment):
        key_id = getattr(settings, "RAZORPAY_KEY_ID", "")
        secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        if not key_id or not secret:
            raise ValidationError("Razorpay credentials are not configured.")
        payload = json.dumps({
            "amount": int(payment.amount * 100),
            "currency": "INR",
            "receipt": payment.order.order_number,
            "notes": {"order_id": str(payment.order_id)},
        }).encode("utf-8")
        auth = base64.b64encode(f"{key_id}:{secret}".encode("utf-8")).decode("ascii")
        request = urllib.request.Request(
            "https://api.razorpay.com/v1/orders",
            data=payload,
            headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        payment.provider_order_id = data["id"]
        payment.save(update_fields=["provider_order_id"])
        return data

    @staticmethod
    def verify_razorpay_signature(payload_body, signature):
        secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        if not secret:
            raise ValidationError("Razorpay secret is not configured.")
        expected = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature or ""):
            raise ValidationError("Invalid Razorpay signature.")

    @staticmethod
    @transaction.atomic
    def confirm_razorpay_payment(payment, provider_order_id, provider_payment_id, signature):
        if payment.method != Payment.Method.RAZORPAY:
            raise ValidationError("Payment is not a Razorpay payment.")
        if not payment.provider_order_id or payment.provider_order_id != provider_order_id:
            raise ValidationError("Razorpay order does not match this payment.")

        secret = getattr(settings, "RAZORPAY_KEY_SECRET", "")
        if not secret:
            raise ValidationError("Razorpay secret is not configured.")
        signed_payload = f"{provider_order_id}|{provider_payment_id}".encode("utf-8")
        expected = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature or ""):
            raise ValidationError("Invalid Razorpay payment signature.")

        payment.provider_payment_id = provider_payment_id
        payment.status = Payment.Status.PAID
        payment.save(update_fields=["provider_payment_id", "status"])
        return payment

    @staticmethod
    @transaction.atomic
    def process_webhook(provider, event_id, event_type, payload, payment=None):
        event, created = WebhookEventLog.objects.get_or_create(
            provider=provider,
            event_id=event_id,
            defaults={
                "event_type": event_type,
                "safe_payload": payload,
                "payment": payment,
                "processing_status": "processing",
            },
        )
        if not created:
            return event
        try:
            if payment and event_type in {"payment.captured", "order.paid"}:
                payment.status = Payment.Status.PAID
                payment.save(update_fields=["status"])
            event.processing_status = "processed"
            event.save(update_fields=["processing_status"])
        except Exception as exc:
            event.processing_status = "failed"
            event.error = str(exc)
            event.save(update_fields=["processing_status", "error"])
            raise
        return event

    @staticmethod
    def parse_payload(raw_body):
        if not raw_body:
            return {}
        return json.loads(raw_body.decode("utf-8"))


class PaymentRecoveryService:
    @staticmethod
    def recover(payment):
        if payment.status == Payment.Status.CREATED and payment.provider_payment_id:
            payment.status = Payment.Status.PAID
            payment.save(update_fields=["status"])
        return payment


class PaymentReconciliationService:
    @staticmethod
    def reconcile(payment, provider_status, provider_amount):
        difference = payment.amount - provider_amount
        reconciliation, _ = PaymentReconciliation.objects.update_or_create(
            payment=payment,
            defaults={
                "provider_status": provider_status,
                "matched": difference == 0 and provider_status in {"paid", "captured", "settled"},
                "difference": difference,
                "reconciled_at": timezone.now(),
            },
        )
        return reconciliation


class CODSettlementService:
    @staticmethod
    def mark_pending(order):
        settlement, _ = CODSettlement.objects.get_or_create(
            order=order,
            defaults={"status": "pending"},
        )
        return settlement

    @staticmethod
    def mark_collected(order, amount):
        settlement, _ = CODSettlement.objects.update_or_create(
            order=order,
            defaults={"collected_amount": amount, "status": "collected"},
        )
        return settlement
