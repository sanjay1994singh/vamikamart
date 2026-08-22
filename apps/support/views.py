from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import SupportTicket


class SupportTicketListView(LoginRequiredMixin, ListView):
    template_name = "support/index.html"

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).order_by("-created_at")
