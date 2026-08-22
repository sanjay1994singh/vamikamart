from django.contrib import admin
from .models import ReturnItem, ReturnRequest


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ("order", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__order_number", "user__email")


admin.site.register(ReturnItem)
