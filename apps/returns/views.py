from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import ReturnRequest


class ReturnRequestListView(LoginRequiredMixin, ListView):
    template_name = "returns/index.html"

    def get_queryset(self):
        return ReturnRequest.objects.filter(user=self.request.user).order_by("-created_at")
