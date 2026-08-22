from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import PriceHistory, Product


@receiver(pre_save, sender=Product)
def record_product_price_history(sender, instance, **kwargs):
    if not instance.pk:
        return
    previous = Product.objects.filter(pk=instance.pk).first()
    if not previous:
        return
    if previous.mrp != instance.mrp or previous.selling_price != instance.selling_price:
        PriceHistory.objects.create(
            product=instance,
            old_mrp=previous.mrp,
            new_mrp=instance.mrp,
            old_selling_price=previous.selling_price,
            new_selling_price=instance.selling_price,
        )
