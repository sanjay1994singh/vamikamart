from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Notification


class NotificationCenterView(LoginRequiredMixin, ListView):
    template_name = "notifications/index.html"
    paginate_by = 30

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")
