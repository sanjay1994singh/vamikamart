from django.contrib.sitemaps import Sitemap
from .models import Category, Product


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.filter(status=Product.Status.ACTIVE)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.filter(active=True)

    def location(self, obj):
        return f"/products/?category={obj.id}"
