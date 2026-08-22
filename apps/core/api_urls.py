from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from .api_views import AddressViewSet, AuthViewSet, BrandViewSet, CartViewSet, CategoryViewSet, NotificationViewSet, OrderViewSet, PaymentViewSet, ProductViewSet, RefundViewSet, ReturnRequestViewSet, ReviewViewSet, SupportTicketViewSet, WishlistViewSet

router = DefaultRouter()
router.register("auth", AuthViewSet, basename="auth")
router.register("categories", CategoryViewSet, basename="category")
router.register("brands", BrandViewSet, basename="brand")
router.register("products", ProductViewSet, basename="product")
router.register("addresses", AddressViewSet, basename="address")
router.register("cart", CartViewSet, basename="cart")
router.register("wishlist", WishlistViewSet, basename="wishlist")
router.register("orders", OrderViewSet, basename="order")
router.register("returns", ReturnRequestViewSet, basename="return")
router.register("refunds", RefundViewSet, basename="refund")
router.register("payments", PaymentViewSet, basename="payment")
router.register("reviews", ReviewViewSet, basename="review")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("support", SupportTicketViewSet, basename="support")

urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("", include(router.urls)),
]
