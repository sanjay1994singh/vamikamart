# Assumptions

- Version 1 is a single-vendor ecommerce business system.
- Default currency is INR.
- PostgreSQL and Redis will be available in the developer environment.
- Razorpay, SMTP, SMS/OTP, courier and object-storage credentials are not available yet.
- The current machine has Python 3.7 only; this project targets Python 3.12+ as required by the prompt.
- Mobile code is intentionally out of scope. The mobile app will use `/api/v1/` later.
