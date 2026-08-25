import json

import pytest
from django.test import override_settings

from apps.accounts.models import User


class FakeGoogleResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def fake_tokeninfo(email="google@example.com"):
    return {
        "aud": "google-client-id",
        "email": email,
        "email_verified": "true",
        "given_name": "Google",
        "family_name": "Customer",
    }


@pytest.mark.django_db
@override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="google-client-id")
def test_google_mobile_creates_customer_account(api_client, monkeypatch):
    monkeypatch.setattr(
        "apps.core.api_views.urllib.request.urlopen",
        lambda *args, **kwargs: FakeGoogleResponse(fake_tokeninfo()),
    )

    response = api_client.post("/api/v1/auth/google_mobile/", {"id_token": "token"}, format="json")

    assert response.status_code == 200
    assert response.data["data"]["access"]
    user = User.objects.get(email="google@example.com")
    assert user.email_verified
    assert not user.has_usable_password()


@pytest.mark.django_db
@override_settings(SOCIAL_AUTH_GOOGLE_OAUTH2_KEY="google-client-id")
def test_google_mobile_reuses_existing_normal_account(api_client, monkeypatch):
    existing = User.objects.create_user(email="normal@example.com", password="pass12345")
    monkeypatch.setattr(
        "apps.core.api_views.urllib.request.urlopen",
        lambda *args, **kwargs: FakeGoogleResponse(fake_tokeninfo("normal@example.com")),
    )

    response = api_client.post("/api/v1/auth/google_mobile/", {"id_token": "token"}, format="json")

    assert response.status_code == 200
    assert response.data["data"]["user"]["id"] == existing.id
    assert User.objects.filter(email="normal@example.com").count() == 1
