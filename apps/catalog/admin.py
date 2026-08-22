from django.contrib import admin
from .models import AttributeValue, Brand, Category, PriceHistory, Product, ProductAttribute, ProductImage, ProductRelation, ProductSpecification, ProductVariant, RecentlyViewedProduct


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "featured", "active", "sort_order")
    list_filter = ("featured", "active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "featured", "active")
    list_filter = ("featured", "active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "brand", "selling_price", "status", "featured", "bestseller", "new_arrival")
    list_filter = ("status", "featured", "bestseller", "new_arrival", "category", "brand")
    search_fields = ("name", "sku", "barcode", "brand__name", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductImageInline, ProductSpecificationInline, ProductVariantInline]


admin.site.register(ProductAttribute)
admin.site.register(AttributeValue)
admin.site.register(PriceHistory)
admin.site.register(ProductRelation)
admin.site.register(RecentlyViewedProduct)
