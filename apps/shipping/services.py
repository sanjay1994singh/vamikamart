from django.utils.crypto import get_random_string
from .models import ShippingManifest


class ShippingService:
    @staticmethod
    def create_manifest(carrier, shipments):
        manifest = ShippingManifest.objects.create(
            manifest_number=f"MAN{get_random_string(10).upper()}",
            carrier=carrier,
        )
        manifest.shipments.set(shipments)
        return manifest
