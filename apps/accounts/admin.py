from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Address, User, VerificationToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "role", "account_status", "email_verified", "mobile_verified", "is_staff")
    list_filter = ("role", "account_status", "email_verified", "mobile_verified", "is_staff")
    search_fields = ("email", "username", "mobile_number", "first_name", "last_name")
    ordering = ("email",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone", "city", "state", "pin_code", "default_shipping", "default_billing")
    list_filter = ("address_type", "state", "default_shipping", "default_billing")
    search_fields = ("full_name", "phone", "user__email", "city", "pin_code")


@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "sent_to", "consumed_at", "expires_at", "created_at")
    list_filter = ("purpose", "consumed_at", "expires_at")
    search_fields = ("user__email", "sent_to", "token")
