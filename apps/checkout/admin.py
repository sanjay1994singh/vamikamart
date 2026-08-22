from django.contrib import admin
from .models import CheckoutQuote, IdempotencyKey


admin.site.register(CheckoutQuote)
admin.site.register(IdempotencyKey)
