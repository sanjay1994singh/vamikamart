# Mobile API Handoff

Base path: `/api/v1/`

Authentication:

- `POST /api/v1/auth/login/` returns JWT access and refresh tokens.
- `POST /api/v1/auth/refresh/` refreshes the access token.
- `POST /api/v1/auth/logout/` blacklists refresh tokens when token blacklisting is enabled.

Implemented starter groups:

- `/api/v1/categories/`
- `/api/v1/brands/`
- `/api/v1/products/`
- `/api/v1/addresses/`
- `/api/v1/cart/current/`
- `/api/v1/cart/add/`
- `/api/v1/cart/update_quantity/`
- `/api/v1/cart/remove/`
- `/api/v1/cart/clear/`
- `/api/v1/cart/apply_coupon/`
- `/api/v1/cart/quote/`
- `/api/v1/cart/place_order/`
- `/api/v1/cart/check_pin/`
- `/api/v1/wishlist/`
- `/api/v1/orders/`
- `/api/v1/orders/{id}/cancel/`
- `/api/v1/payments/`
- `/api/v1/returns/`
- `/api/v1/refunds/`
- `/api/v1/reviews/`
- `/api/v1/notifications/`
- `/api/v1/support/`

Response shape for custom actions:

```json
{
  "success": true,
  "message": "Cart loaded",
  "data": {}
}
```

The React Native app should treat Django as authoritative for price, inventory, coupon, checkout, payment and order state.
