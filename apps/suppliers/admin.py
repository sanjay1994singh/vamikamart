from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("supplier_name", "business_name", "contact_person", "phone", "email", "active")
    list_filter = ("active",)
    search_fields = ("supplier_name", "business_name", "contact_person", "phone", "email", "gst_number")
