from django.contrib import admin
from .models import Banner, HomeSection


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ("key", "title", "active", "sort_order")
    list_filter = ("active",)
    search_fields = ("key", "title")


admin.site.register(Banner)
