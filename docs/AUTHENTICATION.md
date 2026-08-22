# Authentication

The project uses a custom `accounts.User` model. Web authentication should use Django sessions and CSRF protection. Mobile-ready authentication uses Simple JWT endpoints under `/api/v1/auth/`.
