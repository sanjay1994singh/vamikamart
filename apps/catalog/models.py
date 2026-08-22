from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from apps.core.validators import validate_image_upload


class Category(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children")
    image = models.ImageField(upload_to="categories/", blank=True, validators=[validate_image_upload])
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    def clean(self):
        node = self.parent
        while node:
            if node == self:
                raise ValidationError("Category cannot be its own descendant.")
            node = node.parent

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True, validators=[validate_image_upload])
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        OUT_OF_STOCK = "out_of_stock", "Out Of Stock"
        INACTIVE = "inactive", "Inactive"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=220)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=80, unique=True)
    barcode = models.CharField(max_length=80, unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.PROTECT, related_name="products")
    short_description = models.CharField(max_length=320, blank=True)
    full_description = models.TextField(blank=True)
    mrp = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_class = models.CharField(max_length=80, blank=True)
    hsn_sac = models.CharField(max_length=32, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    featured = models.BooleanField(default=False)
    bestseller = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    returnable = models.BooleanField(default=True)
    return_window_days = models.PositiveIntegerField(default=7)
    cod_allowed = models.BooleanField(default=True)
    warranty = models.CharField(max_length=160, blank=True)
    manufacturer = models.CharField(max_length=160, blank=True)
    country_of_origin = models.CharField(max_length=80, default="India")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.status == self.Status.ACTIVE and (not self.name or not self.sku or self.selling_price <= 0):
            raise ValidationError("Active products require name, SKU and positive selling price.")
        if self.status == self.Status.ACTIVE and self.category_id is None:
            raise ValidationError("Active products require a category.")

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"slug": self.slug})

    @property
    def discount_percent(self):
        if self.mrp and self.mrp > self.selling_price:
            return int(((self.mrp - self.selling_price) / self.mrp) * 100)
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", validators=[validate_image_upload])
    alt_text = models.CharField(max_length=180, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)


class ProductAttribute(models.Model):
    name = models.CharField(max_length=100, unique=True)


class AttributeValue(models.Model):
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name="values")
    value = models.CharField(max_length=100)

    class Meta:
        unique_together = ("attribute", "value")


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    values = models.ManyToManyField(AttributeValue, blank=True)
    sku = models.CharField(max_length=80, unique=True)
    barcode = models.CharField(max_length=80, unique=True, null=True, blank=True)
    mrp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    image = models.ImageField(upload_to="variants/", blank=True, validators=[validate_image_upload])
    status = models.CharField(max_length=20, choices=Product.Status.choices, default=Product.Status.ACTIVE)


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications")
    name = models.CharField(max_length=120)
    value = models.CharField(max_length=220)
    sort_order = models.PositiveIntegerField(default=0)


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    old_mrp = models.DecimalField(max_digits=12, decimal_places=2)
    new_mrp = models.DecimalField(max_digits=12, decimal_places=2)
    old_selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    new_selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductRelation(models.Model):
    class RelationType(models.TextChoices):
        RELATED = "related", "Related"
        SIMILAR = "similar", "Similar"
        FREQUENTLY_BOUGHT = "frequently_bought", "Frequently Bought Together"
        ACCESSORY = "accessory", "Accessory"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="relations")
    related_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="related_to")
    relation_type = models.CharField(max_length=32, choices=RelationType.choices)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "related_product", "relation_type")


class RecentlyViewedProduct(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=80, blank=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "session_key", "product")
