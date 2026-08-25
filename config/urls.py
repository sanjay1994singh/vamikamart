from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.catalog.sitemaps import CategorySitemap, ProductSitemap
from apps.catalog.views import HomeView, ProductDetailView, ProductListView
from apps.accounts.views import AccountPasswordChangeView, AddressCreateView, AddressDefaultView, ProfileView, RegisterView
from apps.analytics.views import action_queues, order_filters, owner_dashboard, owner_search, reports
from apps.carts.views import CartPageView
from apps.checkout.views import CheckoutPageView
from apps.core.views import latest_android_app_download, mobile_google_login_done, mobile_google_login_start, mobile_product_open, robots_txt
from apps.orders.views import OrderDetailPageView, OrderListPageView, invoice_view
from apps.notifications.views import NotificationCenterView
from apps.returns.views import ReturnRequestListView
from apps.support.views import SupportTicketListView
from apps.wishlist.views import WishlistPageView
from apps.payments.views import razorpay_webhook
from apps.shipping.views import manifest_view, packing_slip, shipping_label

sitemaps = {"products": ProductSitemap, "categories": CategorySitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("cart/", CartPageView.as_view(), name="cart"),
    path("checkout/", CheckoutPageView.as_view(), name="checkout"),
    path("orders/", OrderListPageView.as_view(), name="orders"),
    path("orders/<int:pk>/", OrderDetailPageView.as_view(), name="order-web-detail"),
    path("orders/<int:order_id>/invoice/", invoice_view, name="order-invoice"),
    path("notifications/", NotificationCenterView.as_view(), name="notifications"),
    path("returns/", ReturnRequestListView.as_view(), name="returns"),
    path("support/", SupportTicketListView.as_view(), name="support"),
    path("wishlist/", WishlistPageView.as_view(), name="wishlist"),
    path("owner/orders/<int:order_id>/packing-slip/", packing_slip, name="packing-slip"),
    path("owner/orders/<int:order_id>/shipping-label/", shipping_label, name="shipping-label"),
    path("owner/orders/<int:order_id>/invoice/", invoice_view, name="invoice"),
    path("owner/manifests/<int:manifest_id>/", manifest_view, name="manifest"),
    path("owner/dashboard/", owner_dashboard, name="owner-dashboard"),
    path("owner/reports/", reports, name="owner-reports"),
    path("owner/action-queues/", action_queues, name="owner-action-queues"),
    path("owner/search/", owner_search, name="owner-search"),
    path("owner/order-filters/", order_filters, name="owner-order-filters"),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("accounts/register/", RegisterView.as_view(), name="register"),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
    path("accounts/addresses/add/", AddressCreateView.as_view(), name="address-add"),
    path("accounts/addresses/<int:pk>/default/", AddressDefaultView.as_view(), name="address-default"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/change-password/", AccountPasswordChangeView.as_view(), name="change_password"),
    path("accounts/password-reset/", auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), name="password_reset"),
    path("accounts/password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_done"),
    path("auth/", include("social_django.urls", namespace="social")),
    path("mobile/auth/google/start/", mobile_google_login_start, name="mobile-google-login-start"),
    path("mobile/auth/google/done/", mobile_google_login_done, name="mobile-google-login-done"),
    path("app/open/product/<slug:slug>/", mobile_product_open, name="mobile-product-open"),
    path("app/download/", latest_android_app_download, name="app-download"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/", include("apps.core.api_urls")),
    path("webhooks/razorpay/", razorpay_webhook, name="razorpay-webhook"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
