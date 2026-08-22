from django.contrib import admin
from .models import ActionQueueItem, AuditLog, CustomerMetricSnapshot, CustomerTimelineEvent, OperationalExpense


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "entity", "object_id", "actor", "created_at")
    list_filter = ("action", "entity", "created_at")
    search_fields = ("action", "entity", "object_id", "actor__email")
    readonly_fields = ("created_at",)


admin.site.register(OperationalExpense)
admin.site.register(CustomerTimelineEvent)
admin.site.register(CustomerMetricSnapshot)
admin.site.register(ActionQueueItem)
