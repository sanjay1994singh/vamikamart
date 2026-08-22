# Architecture

The backend is a modular Django monolith. Django owns the commerce database and is the single source of truth for customers, catalog, inventory, carts, checkout, orders, payments, support and future mobile API state.

Website pages are rendered with Django templates. DRF exposes `/api/v1/` for future React Native clients. Both web views and APIs should call service classes for business decisions instead of duplicating commerce calculations.

Key services currently established:

- `InventoryService` for stock reservation/release with `transaction.atomic()` and `select_for_update()`.
- `PricingService`, `CouponService` and `CheckoutService` for Decimal-based totals.
- `OrderService` for cart-to-order creation and stock reservation.

PostgreSQL is the intended production database. Redis powers Celery and future cache/reservation expiry jobs.
