from django.utils import timezone
from celery import shared_task
from apps.notifications.services import NotificationService
from .models import AbandonedCartReminder, Cart


@shared_task
def schedule_abandoned_cart_reminders():
    cutoff = timezone.now() - timezone.timedelta(hours=2)
    for cart in Cart.objects.filter(updated_at__lt=cutoff, items__isnull=False, user__isnull=False).distinct():
        AbandonedCartReminder.objects.get_or_create(
            cart=cart,
            sent_at=None,
            defaults={"scheduled_at": timezone.now() + timezone.timedelta(minutes=5)},
        )


@shared_task
def send_due_abandoned_cart_reminders():
    due = AbandonedCartReminder.objects.filter(sent_at__isnull=True, scheduled_at__lte=timezone.now()).select_related("cart__user")
    for reminder in due:
        NotificationService.create(reminder.cart.user, "Items waiting in your cart", "Complete checkout before stock or prices change.")
        reminder.sent_at = timezone.now()
        reminder.save(update_fields=["sent_at"])
