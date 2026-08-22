from django.contrib import admin
from .models import BusinessProfile, StaffProfile, StaffRole


admin.site.register(BusinessProfile)
admin.site.register(StaffRole)
admin.site.register(StaffProfile)
