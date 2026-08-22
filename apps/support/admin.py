from django.contrib import admin
from .models import SupportMessage, SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("subject", "user__email")


admin.site.register(SupportMessage)
