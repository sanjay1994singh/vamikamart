import json
import urllib.parse
import urllib.request
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import Address, User
from apps.accounts.services import VerificationService
from apps.accounts.models import VerificationToken
from apps.catalog.models import Brand, Category, Product, ProductVariant
from apps.carts.models import Cart, CartItem
from apps.carts.services import CartService
from apps.checkout.services import CheckoutService
from apps.checkout.models import CheckoutQuote, IdempotencyKey
from apps.orders.models import Order
from apps.orders.services import OrderService
from apps.analytics.audit import AuditService
from apps.notifications.models import Notification
from apps.payments.models import Payment
from apps.payments.services import CODSettlementService, PaymentRecoveryService, PaymentService
from apps.promotions.models import Coupon
from apps.inventory.models import WarehouseInventory
from apps.refunds.models import Refund
from apps.returns.models import ReturnRequest
from apps.reviews.models import Review
from apps.support.models import SupportTicket
from apps.wishlist.models import WishlistItem
from .serializers import (
    AddressSerializer,
    BrandSerializer,
    CartMutationSerializer,
    CartSerializer,
    CategorySerializer,
    CheckoutQuoteSerializer,
    CouponApplySerializer,
    GoogleTokenSerializer,
    OrderSerializer,
    PlaceOrderSerializer,
    PaymentSerializer,
    PinCheckSerializer,
    ProductSerializer,
    RazorpayConfirmSerializer,
    RefundSerializer,
    RegisterSerializer,
    ReturnRequestSerializer,
    ReviewSerializer,
    SupportTicketSerializer,
    UserSerializer,
    TokenConsumeSerializer,
    WishlistItemSerializer,
    NotificationSerializer,
)


def ok(message, data=None):
    return Response({"success": True, "message": message, "data": data or {}})


def fail(message, errors=None, http_status=status.HTTP_400_BAD_REQUEST):
    return Response({"success": False, "message": message, "errors": errors or {}}, status=http_status)


def checkout_payload(summary):
    return {
        "lines": [
            {
                "item_id": line["item"].id,
                "product_id": line["item"].product_id,
                "product_name": line["item"].product.name,
                "variant_id": line["item"].variant_id,
                "quantity": line["item"].quantity,
                "unit_price": line["unit_price"],
                "line_total": line["line_total"],
            }
            for line in summary["lines"]
        ],
        "mrp_total": summary["mrp_total"],
        "subtotal": summary["subtotal"],
        "coupon_discount": summary["coupon_discount"],
        "tax": summary["tax"],
        "shipping": summary["shipping"],
        "final_total": summary["final_total"],
    }


def json_ready(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    return value


def available_quantity(product, variant=None):
    total = 0
    for inv in WarehouseInventory.objects.filter(product=product, variant=variant):
        total += inv.available_stock
    return total


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return ok("Registration successful", UserSerializer(user).data)

    @action(detail=False, methods=["post"])
    def google_mobile(self, request):
        serializer = GoogleTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["id_token"]
        try:
            query = urllib.parse.urlencode({"id_token": token})
            with urllib.request.urlopen(f"https://oauth2.googleapis.com/tokeninfo?{query}", timeout=10) as response:
                profile = json.loads(response.read().decode("utf-8"))
        except Exception:
            return fail("Google sign-in failed", {"google": ["Could not verify Google token."]}, status.HTTP_400_BAD_REQUEST)

        if profile.get("aud") != settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY:
            return fail("Google sign-in failed", {"google": ["Google token audience does not match this app."]}, status.HTTP_400_BAD_REQUEST)
        email = User.objects.normalize_email(profile.get("email", ""))
        if not email:
            return fail("Google sign-in failed", {"email": ["Google account did not return an email."]}, status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            email__iexact=email,
            defaults={
                "email": email,
                "username": User.objects.available_username(email),
                "first_name": profile.get("given_name", ""),
                "last_name": profile.get("family_name", ""),
                "email_verified": profile.get("email_verified") in {True, "true", "True", "1"},
            },
        )
        if created:
            user.set_unusable_password()
            user.save()
        elif profile.get("email_verified") in {True, "true", "True", "1"} and not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified"])

        refresh = RefreshToken.for_user(user)
        return ok("Google login successful", {
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })

    @action(detail=False, methods=["get", "patch", "put"], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        if request.method in {"PATCH", "PUT"}:
            serializer = UserSerializer(request.user, data=request.data, partial=request.method == "PATCH")
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return ok("Profile updated", serializer.data)
        return ok("Profile loaded", UserSerializer(request.user).data)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def send_email_verification(self, request):
        token = VerificationService.issue_email_verification(request.user)
        return ok("Email verification token issued", {"token": token.token})

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def verify_email(self, request):
        serializer = TokenConsumeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = VerificationService.consume(serializer.validated_data["token"], VerificationToken.Purpose.EMAIL)
        if not user:
            return fail("Invalid verification token", {"token": ["Invalid or expired token."]})
        return ok("Email verified", UserSerializer(user).data)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def send_mobile_otp(self, request):
        token = VerificationService.issue_mobile_otp(request.user)
        return ok("Mobile OTP issued", {"otp": token.token})

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def verify_mobile(self, request):
        serializer = TokenConsumeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = VerificationService.consume(serializer.validated_data["token"], VerificationToken.Purpose.MOBILE)
        if not user:
            return fail("Invalid OTP", {"token": ["Invalid or expired OTP."]})
        return ok("Mobile verified", UserSerializer(user).data)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer
    lookup_field = "slug"


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.filter(active=True)
    serializer_class = BrandSerializer
    lookup_field = "slug"


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(status=Product.Status.ACTIVE).select_related("category", "brand").prefetch_related("images", "variants").order_by("-created_at")
    serializer_class = ProductSerializer
    lookup_field = "slug"
    filterset_fields = ["category", "brand", "featured", "bestseller", "new_arrival"]
    search_fields = ["name", "sku", "brand__name", "category__name"]


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Address.objects.none()
        return Address.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Cart.objects.none()
        if not self.request.user.is_authenticated:
            return CartService.get_or_create_for_request(self.request).__class__.objects.filter(session_key=self.request.session.session_key, user=None).order_by("-updated_at")
        return Cart.objects.filter(user=self.request.user).prefetch_related("items__product").order_by("-updated_at")

    @action(detail=False, methods=["get"])
    def current(self, request):
        cart = CartService.get_or_create_for_request(request)
        return ok("Cart loaded", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def add(self, request):
        serializer = CartMutationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        product = get_object_or_404(Product, id=data["product_id"], status=Product.Status.ACTIVE)
        variant = None
        if data.get("variant_id"):
            variant = get_object_or_404(ProductVariant, id=data["variant_id"], product=product, status=Product.Status.ACTIVE)
        cart = CartService.get_or_create_for_request(request)
        if available_quantity(product, variant) < data["quantity"]:
            return fail("Insufficient stock", {"quantity": ["Requested quantity is not available."]})
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, variant=variant, defaults={"quantity": data["quantity"]})
        if not created:
            if available_quantity(product, variant) < item.quantity + data["quantity"]:
                return fail("Insufficient stock", {"quantity": ["Requested quantity is not available."]})
            item.quantity += data["quantity"]
            item.save(update_fields=["quantity"])
        return ok("Product added to cart", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def update_quantity(self, request):
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity", 1))
        if quantity < 1:
            return fail("Quantity must be at least 1", {"quantity": ["Minimum quantity is 1."]})
        cart = CartService.get_or_create_for_request(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        if available_quantity(item.product, item.variant) < quantity:
            return fail("Insufficient stock", {"quantity": ["Requested quantity is not available."]})
        item.quantity = quantity
        item.save(update_fields=["quantity"])
        return ok("Cart quantity updated", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def remove(self, request):
        cart = CartService.get_or_create_for_request(request)
        CartItem.objects.filter(id=request.data.get("item_id"), cart=cart).delete()
        return ok("Cart item removed", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def save_for_later(self, request):
        cart = CartService.get_or_create_for_request(request)
        item = get_object_or_404(CartItem, id=request.data.get("item_id"), cart=cart)
        item.saved_for_later = True
        item.save(update_fields=["saved_for_later"])
        return ok("Item saved for later", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def move_to_cart(self, request):
        cart = CartService.get_or_create_for_request(request)
        item = get_object_or_404(CartItem, id=request.data.get("item_id"), cart=cart)
        item.saved_for_later = False
        item.save(update_fields=["saved_for_later"])
        return ok("Item moved to cart", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def move_to_wishlist(self, request):
        if not request.user.is_authenticated:
            return fail("Login required", {"auth": ["Please log in to use wishlist."]}, status.HTTP_401_UNAUTHORIZED)
        cart = CartService.get_or_create_for_request(request)
        item = get_object_or_404(CartItem, id=request.data.get("item_id"), cart=cart)
        WishlistItem.objects.get_or_create(user=request.user, product=item.product, variant=item.variant)
        item.delete()
        return ok("Item moved to wishlist", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def clear(self, request):
        cart = CartService.get_or_create_for_request(request)
        cart.items.all().delete()
        return ok("Cart cleared", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def apply_coupon(self, request):
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.is_authenticated:
            return fail("Login required", {"auth": ["Please log in to apply coupons."]}, status.HTTP_401_UNAUTHORIZED)
        cart = CartService.get_or_create_for_request(request)
        coupon = get_object_or_404(Coupon, code__iexact=serializer.validated_data["code"])
        cart.coupon = coupon
        cart.save(update_fields=["coupon"])
        try:
            summary = CheckoutService.summarize(cart)
        except ValidationError as exc:
            cart.coupon = None
            cart.save(update_fields=["coupon"])
            return fail("Coupon could not be applied", {"coupon": exc.messages})
        return ok("Coupon applied", checkout_payload(summary))

    @action(detail=False, methods=["post"])
    def quote(self, request):
        serializer = CheckoutQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = CartService.get_or_create_for_request(request)
        summary = CheckoutService.summarize(cart)
        payload = checkout_payload(summary)
        CheckoutQuote.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key or "",
            cart=cart,
            totals=json_ready(payload),
            expires_at=timezone.now() + timezone.timedelta(minutes=15),
        )
        return ok("Checkout quote generated", payload)

    @action(detail=False, methods=["post"])
    def place_order(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.is_authenticated:
            return fail("Login required", {"auth": ["Please log in to place order."]}, status.HTTP_401_UNAUTHORIZED)
        idem_key = request.headers.get("Idempotency-Key")
        if idem_key:
            existing = IdempotencyKey.objects.filter(key=idem_key, user=request.user).first()
            if existing and existing.response_data:
                return ok("Order already placed", existing.response_data)
        cart = CartService.get_or_create_for_request(request)
        if not cart.items.exists():
            return fail("Cart is empty", {"cart": ["Add products before checkout."]})
        address = get_object_or_404(Address, id=serializer.validated_data["address_id"], user=request.user)
        try:
            order = OrderService.create_from_cart(cart, address, request.user)
        except ValidationError as exc:
            return fail("Order could not be created", {"stock": exc.messages})
        Payment.objects.create(order=order, method=serializer.validated_data["payment_method"], amount=order.grand_total)
        payment = order.payment
        provider_data = {}
        if payment.method == Payment.Method.COD:
            CODSettlementService.mark_pending(order)
        elif payment.method == Payment.Method.RAZORPAY:
            try:
                provider_data = PaymentService.create_razorpay_order(payment)
                provider_data["key_id"] = settings.RAZORPAY_KEY_ID
            except ValidationError as exc:
                provider_data = {"credentials_required": True, "error": exc.messages}
            except Exception:
                provider_data = {"credentials_required": True, "error": ["Razorpay order could not be created."]}
        cart.items.all().delete()
        data = OrderSerializer(order, context={"request": request}).data
        data["payment"] = PaymentSerializer(payment).data
        data["provider"] = provider_data
        if idem_key:
            IdempotencyKey.objects.update_or_create(key=idem_key, user=request.user, defaults={"response_data": data})
        return ok("Order placed", data)

    @action(detail=False, methods=["post"])
    def buy_now(self, request):
        if not request.user.is_authenticated:
            return fail("Login required", {"auth": ["Please log in to buy now."]}, status.HTTP_401_UNAUTHORIZED)
        serializer = CartMutationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = get_object_or_404(Product, id=serializer.validated_data["product_id"], status=Product.Status.ACTIVE)
        variant = None
        if serializer.validated_data.get("variant_id"):
            variant = get_object_or_404(ProductVariant, id=serializer.validated_data["variant_id"], product=product, status=Product.Status.ACTIVE)
        if available_quantity(product, variant) < serializer.validated_data["quantity"]:
            return fail("Insufficient stock", {"quantity": ["Requested quantity is not available."]})
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.filter(saved_for_later=False).delete()
        CartItem.objects.create(cart=cart, product=product, variant=variant, quantity=serializer.validated_data["quantity"])
        return ok("Buy now cart prepared", CartSerializer(cart, context={"request": request}).data)

    @action(detail=False, methods=["post"])
    def check_pin(self, request):
        from apps.shipping.rates import ShippingRateService

        serializer = PinCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serviceable = ShippingRateService.is_pin_serviceable(serializer.validated_data["pin_code"])
        return ok("PIN checked", {"serviceable": serviceable})


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        from apps.orders.models import CancellationRequest

        order = self.get_object()
        if order.status not in {Order.Status.PENDING, Order.Status.CONFIRMED}:
            return fail("Order cannot be cancelled", {"status": ["Current status is not cancellable."]})
        CancellationRequest.objects.create(order=order, requested_by=request.user, reason=request.data.get("reason", "Customer requested cancellation"), refund_amount=order.grand_total)
        AuditService.log("cancellation_requested", "orders.Order", order.id, actor=request.user, new={"status": order.status})
        return ok("Cancellation requested")


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return SupportTicket.objects.none()
        return SupportTicket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return WishlistItem.objects.none()
        return WishlistItem.objects.filter(user=self.request.user).select_related("product", "variant")

    @action(detail=False, methods=["post"])
    def add(self, request):
        serializer = CartMutationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        product = get_object_or_404(Product, id=data["product_id"], status=Product.Status.ACTIVE)
        variant = None
        if data.get("variant_id"):
            variant = get_object_or_404(ProductVariant, id=data["variant_id"], product=product, status=Product.Status.ACTIVE)
        WishlistItem.objects.get_or_create(user=request.user, product=product, variant=variant)
        return ok("Product added to wishlist")

    @action(detail=False, methods=["post"])
    def remove(self, request):
        WishlistItem.objects.filter(id=request.data.get("item_id"), user=request.user).delete()
        return ok("Wishlist item removed")


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(approved=True).select_related("product", "user")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, approved=False)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        from django.utils import timezone
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
        return ok("Notification marked read")


class ReturnRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ReturnRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return ReturnRequest.objects.none()
        return ReturnRequest.objects.filter(user=self.request.user).select_related("order")

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        if order.user_id != self.request.user.id:
            raise ValidationError("Invalid order.")
        serializer.save(user=self.request.user)


class RefundViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Refund.objects.none()
        return Refund.objects.filter(order__user=self.request.user).select_related("order", "payment")


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()
        return Payment.objects.filter(order__user=self.request.user).select_related("order")

    @action(detail=True, methods=["post"])
    def recover(self, request, pk=None):
        payment = self.get_object()
        payment = PaymentRecoveryService.recover(payment)
        return ok("Payment recovery checked", PaymentSerializer(payment).data)

    @action(detail=True, methods=["post"])
    def confirm_razorpay(self, request, pk=None):
        serializer = RazorpayConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = self.get_object()
        try:
            payment = PaymentService.confirm_razorpay_payment(
                payment,
                serializer.validated_data["razorpay_order_id"],
                serializer.validated_data["razorpay_payment_id"],
                serializer.validated_data["razorpay_signature"],
            )
        except ValidationError as exc:
            return fail("Payment could not be verified", {"payment": exc.messages})
        return ok("Payment verified", PaymentSerializer(payment).data)
