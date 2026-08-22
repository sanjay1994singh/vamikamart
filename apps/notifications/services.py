from .models import Notification


class NotificationService:
    @staticmethod
    def create(user, title, body="", metadata=None):
        return Notification.objects.create(user=user, title=title, body=body)

    @staticmethod
    def mark_read(notification, when):
        notification.read_at = when
        notification.save(update_fields=["read_at"])
        return notification
