from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView
from .models import Category, Product, RecentlyViewedProduct


class HomeView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_products"] = Product.objects.filter(status=Product.Status.ACTIVE, featured=True)[:12]
        context["categories"] = Category.objects.filter(active=True, featured=True)[:8]
        return context


class ProductListView(ListView):
    template_name = "catalog/product_list.html"
    model = Product
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.select_related("category", "brand").filter(status=Product.Status.ACTIVE)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(sku__icontains=query) | Q(brand__name__icontains=query))
        return qs.order_by("-created_at")


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
