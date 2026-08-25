from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from apps.core.validators import validate_image_upload


class EmailUserManager(UserManager):
    def available_username(self, email):
        base = (email.split("@", 1)[0] or "user")[:140]
        username = base
        suffix = 1
        while self.model.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base[:140 - len(str(suffix))]}{suffix}"
        return username

    def _create_user(self, email, password, username="", **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        username = username or self.available_username(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, username="", **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, username, **extra_fields)

    def create_superuser(self, email, password=None, username="", **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.OWNER)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, username, **extra_fields)


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
    REQUIRED_FIELDS = []
    objects = EmailUserManager()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = User.objects.normalize_email(self.email)
        if not self.username and self.email:
            self.username = User.objects.available_username(self.email)
        super().save(*args, **kwargs)


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        updates = {}
        if self.default_shipping:
            updates["default_shipping"] = False
        if self.default_billing:
            updates["default_billing"] = False
        if updates:
            Address.objects.filter(user=self.user).exclude(pk=self.pk).update(**updates)


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
