from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from .models import Payment
from .services import PaymentService


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    signature = request.headers.get("X-Razorpay-Signature", "")
    try:
        PaymentService.verify_razorpay_signature(request.body, signature)
        payload = PaymentService.parse_payload(request.body)
        event_id = payload.get("event_id") or payload.get("id") or payload.get("created_at")
        event_type = payload.get("event", "unknown")
        payment_id = payload.get("payload", {}).get("payment", {}).get("entity", {}).get("id", "")
        payment = Payment.objects.filter(provider_payment_id=payment_id).first()
        PaymentService.process_webhook("razorpay", str(event_id), event_type, payload, payment)
    except ValidationError as exc:
        return JsonResponse({"success": False, "message": "Invalid webhook", "errors": exc.messages}, status=400)
    return JsonResponse({"success": True, "message": "Webhook processed"})
