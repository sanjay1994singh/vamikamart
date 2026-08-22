# Django Ecommerce Backend

This folder contains the Django web application and central commerce engine for the ecommerce project. The customer website uses Django templates, while `/api/v1/` exposes DRF endpoints for a future React Native app using the same users, catalog, cart, orders and support records.

## Local Development

1. Install Python 3.12+.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and update PostgreSQL/Redis settings.
5. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Seed demo data:

```bash
python manage.py seed_demo
```

7. Start Django:

```bash
python manage.py runserver
```

8. Start background workers when Redis is running:

```bash
celery -A config worker -l info
celery -A config beat -l info
```

## Useful URLs

- Website: `/`
- Products: `/products/`
- Admin/owner system: `/admin/`
- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- Redoc: `/api/redoc/`

## Status

This is a production-oriented Django ecommerce backend inside `backend`. It includes modular apps, migrations, service layers, customer website pages, DRF APIs, admin registrations, demo data, and initial automated tests.

Verified locally with the project virtualenv:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py seed_demo
pytest
```

Latest result: system check passed, migrations applied, demo data created, and 10 tests passed.

External credentials still required for live integrations:

- Razorpay key/secret
- SMTP credentials
- SMS/OTP provider credentials
- Courier provider credentials
- Object storage/CDN credentials
