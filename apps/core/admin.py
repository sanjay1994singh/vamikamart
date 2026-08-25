from django.contrib import admin
from .models import MobileAppBuild


@admin.register(MobileAppBuild)
class MobileAppBuildAdmin(admin.ModelAdmin):
    list_display = ("version_name", "version_code", "platform", "track", "active", "force_update", "created_at")
    list_filter = ("platform", "track", "active", "force_update")
    search_fields = ("version_name", "version_code", "release_notes")
    readonly_fields = ("created_at",)
    ordering = ("-version_code", "-created_at")
