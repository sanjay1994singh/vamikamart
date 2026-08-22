# Security

Implemented foundations:

- Custom user model from project start.
- Session and JWT authentication support.
- CSRF middleware for web forms.
- Customer-scoped querysets for addresses, cart, orders and support.
- Internal fields such as product cost price are excluded from public serializers/templates.
- Inventory reservation uses database locks to reduce overselling risk.

Still required:

- Rate limiting for auth and sensitive endpoints.
- File MIME/dimension validation.
- Razorpay webhook signature verification.
- Full permission matrix tests for staff roles.
