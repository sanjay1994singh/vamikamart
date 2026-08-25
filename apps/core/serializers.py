from rest_framework import serializers
from apps.accounts.models import Address, User
from apps.catalog.models import Brand, Category, Product, ProductImage, ProductVariant
from apps.carts.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.notifications.models import Notification
from apps.payments.models import Payment
from apps.refunds.models import Refund
from apps.returns.models import ReturnRequest
from apps.reviews.models import Review
from apps.promotions.models import Coupon
from apps.support.models import SupportTicket
from apps.wishlist.models import WishlistItem


class ApiResponseMixin:
    pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "mobile_number",
            "date_of_birth",
            "gender",
            "role",
            "email_verified",
            "mobile_verified",
        ]
        read_only_fields = ["email", "role", "email_verified", "mobile_verified"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name", "mobile_number", "password"]

    def validate_email(self, value):
        email = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["user"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent", "image", "description", "featured"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "logo", "description", "featured"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text", "is_primary", "sort_order"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "sku", "mrp", "selling_price", "image", "status"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "sku", "category", "brand", "short_description",
            "full_description", "mrp", "selling_price", "featured", "bestseller",
            "new_arrival", "returnable", "return_window_days", "cod_allowed",
            "warranty", "manufacturer", "country_of_origin", "images", "variants",
            "discount_percent",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "variant", "quantity", "saved_for_later"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "coupon", "updated_at"]


class CartMutationSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class CouponApplySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=40)


class CheckoutQuoteSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(required=False)


class PlaceOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=["cod", "razorpay"])


class TokenConsumeSerializer(serializers.Serializer):
    token = serializers.CharField()


class GoogleTokenSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class PinCheckSerializer(serializers.Serializer):
    pin_code = serializers.CharField(max_length=12)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product_name", "sku", "quantity", "unit_price", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "order_number", "status", "subtotal", "coupon_discount", "tax", "shipping", "grand_total", "items", "created_at"]


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ["id", "subject", "message", "status", "created_at"]
        read_only_fields = ["status"]


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "variant", "created_at"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "product", "rating", "title", "body", "approved", "created_at"]
        read_only_fields = ["approved"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "body", "read_at", "created_at"]


class ReturnRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = ["id", "order", "reason", "status", "created_at"]
        read_only_fields = ["status"]


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ["id", "order", "payment", "amount", "status", "provider_refund_id", "created_at"]
        read_only_fields = ["payment", "amount", "status", "provider_refund_id"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order", "method", "status", "provider_order_id", "provider_payment_id", "amount", "created_at"]
        read_only_fields = ["status", "provider_order_id", "provider_payment_id", "amount"]


class RazorpayConfirmSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()
