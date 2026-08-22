from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.validators import validate_image_upload


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        OWNER = "owner", "Business Owner"
        STAFF = "staff", "Staff"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        DELETED = "deleted", "Deleted"

    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, validators=[validate_image_upload])
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    email_verified = models.BooleanField(default=False)
    mobile_verified = models.BooleanField(default=False)
    account_status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class Address(models.Model):
    class AddressType(models.TextChoices):
        HOME = "home", "Home"
        WORK = "work", "Work"
        OTHER = "other", "Other"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    house = models.CharField(max_length=160)
    street = models.CharField(max_length=160)
    landmark = models.CharField(max_length=160, blank=True)
    locality = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    district = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120)
    country = models.CharField(max_length=80, default="India")
    pin_code = models.CharField(max_length=12)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address_type = models.CharField(max_length=20, choices=AddressType.choices, default=AddressType.HOME)
    default_shipping = models.BooleanField(default=False)
    default_billing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class VerificationToken(models.Model):
    class Purpose(models.TextChoices):
        EMAIL = "email", "Email"
        MOBILE = "mobile", "Mobile"
        PASSWORD_RESET = "password_reset", "Password Reset"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_tokens")
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    token = models.CharField(max_length=80, unique=True)
    sent_to = models.CharField(max_length=180)
    consumed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
