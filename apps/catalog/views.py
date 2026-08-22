from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView
from .models import Category, Product, RecentlyViewedProduct

STORE_PROMISES = [
    {"label": "Smart weekly basket", "text": "Staples grouped so repeat orders take less effort.", "image": "weekly-basket"},
    {"label": "Fresh-first picks", "text": "Produce, dairy and bakery sections stay easy to scan.", "image": "fresh-picks"},
    {"label": "No noisy checkout", "text": "Simple cart, clear prices and support when you need it.", "image": "easy-checkout"},
]

DUMMY_CATEGORIES = [
    {"name": "Fresh Produce", "image": "fresh-produce"},
    {"name": "Milk & Breakfast", "image": "milk-breakfast"},
    {"name": "Kitchen Staples", "image": "kitchen-staples"},
    {"name": "Ready Snacks", "image": "ready-snacks"},
    {"name": "Drinks & Coolers", "image": "drinks-coolers"},
    {"name": "Tea & Coffee", "image": "tea-coffee"},
    {"name": "Bakery Shelf", "image": "bakery-shelf"},
    {"name": "Sweet Cravings", "image": "sweet-cravings"},
    {"name": "Baby & Family", "image": "baby-family"},
    {"name": "Health Basics", "image": "health-basics"},
    {"name": "Home Cleaning", "image": "home-cleaning"},
    {"name": "Personal Care", "image": "personal-care"},
    {"name": "Pet Supplies", "image": "pet-supplies"},
    {"name": "Office Needs", "image": "office-needs"},
    {"name": "Organic Picks", "image": "organic-picks"},
    {"name": "Weekend Specials", "image": "weekend-specials"},
]

DUMMY_PRODUCTS = [
    {"name": "Robusta Banana", "sku": "VM-DUMMY-BANANA", "size": "6 pcs", "price": 42, "mrp": 55, "tag": "Fresh", "image": "banana"},
    {"name": "Toned Milk Pouch", "sku": "VM-DUMMY-MILK", "size": "500 ml", "price": 29, "mrp": 32, "tag": "Dairy", "image": "milk"},
    {"name": "Soft Sandwich Bread", "sku": "VM-DUMMY-BREAD", "size": "400 g", "price": 45, "mrp": 50, "tag": "Bakery", "image": "bread"},
    {"name": "Farm Potato", "sku": "VM-DUMMY-POTATO", "size": "1 kg", "price": 38, "mrp": 48, "tag": "Veg", "image": "potato"},
    {"name": "Orange Cooler", "sku": "VM-DUMMY-ORANGE", "size": "1 L", "price": 109, "mrp": 130, "tag": "Drink", "image": "orange-drink"},
    {"name": "Masala Wafer Pack", "sku": "VM-DUMMY-SNACK", "size": "82 g", "price": 20, "mrp": 20, "tag": "Snack", "image": "snack"},
    {"name": "Corn Flakes", "sku": "VM-DUMMY-CORNFLAKES", "size": "250 g", "price": 115, "mrp": 135, "tag": "Meal", "image": "corn-flakes"},
    {"name": "Dark Chocolate Bar", "sku": "VM-DUMMY-CHOCOLATE", "size": "60 g", "price": 89, "mrp": 99, "tag": "Sweet", "image": "chocolate"},
    {"name": "Daily Basmati Rice", "sku": "VM-DUMMY-RICE", "size": "1 kg", "price": 145, "mrp": 170, "tag": "Staple", "image": "rice"},
    {"name": "Laundry Detergent", "sku": "VM-DUMMY-DETERGENT", "size": "1 kg", "price": 178, "mrp": 210, "tag": "Home", "image": "detergent"},
]


def dummy_products_with_ids():
    products = {product.sku: product.id for product in Product.objects.filter(sku__startswith="VM-DUMMY-")}
    return [{**item, "product_id": products.get(item["sku"])} for item in DUMMY_PRODUCTS]


class HomeView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        real_products = Product.objects.select_related("category").filter(status=Product.Status.ACTIVE, featured=True).exclude(sku__startswith="VM-DUMMY-")
        featured_products = real_products[:12]
        categories = Category.objects.filter(active=True, featured=True).exclude(slug__startswith="vm-dummy-")[:20]
        context["featured_products"] = featured_products
        context["categories"] = categories
        context["show_dummy_storefront"] = real_products.count() < 8 or categories.count() < 8
        context["store_promises"] = STORE_PROMISES
        context["dummy_categories"] = DUMMY_CATEGORIES
        context["dummy_products"] = dummy_products_with_ids()
        return context


class ProductListView(ListView):
    template_name = "catalog/product_list.html"
    model = Product
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.select_related("category", "brand").filter(status=Product.Status.ACTIVE).exclude(sku__startswith="VM-DUMMY-")
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(sku__icontains=query) | Q(brand__name__icontains=query))
        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["dummy_products"] = dummy_products_with_ids()
        context["show_dummy_storefront"] = not context["object_list"]
        return context


class ProductDetailView(DetailView):
    template_name = "catalog/product_detail.html"
    queryset = Product.objects.prefetch_related("images", "variants__values", "specifications").filter(status=Product.Status.ACTIVE)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        try:
            if self.request.user.is_authenticated:
                RecentlyViewedProduct.objects.update_or_create(user=self.request.user, product=obj, defaults={"session_key": ""})
            elif self.request.session.session_key:
                RecentlyViewedProduct.objects.update_or_create(session_key=self.request.session.session_key, product=obj, defaults={"user": None})
        except Exception:
            pass
        return obj
