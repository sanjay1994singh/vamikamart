from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from apps.carts.services import CartService


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    CartService.merge_guest_cart(request, user)
