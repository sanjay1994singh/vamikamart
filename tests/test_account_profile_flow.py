import pytest

from apps.accounts.models import Address, User


@pytest.mark.django_db
def test_registration_logs_customer_in_with_multiple_auth_backends(client):
    response = client.post(
        "/accounts/register/",
        {
            "email": "newweb@example.com",
            "first_name": "New",
            "mobile_number": "9999999999",
            "password1": "S8rong!Pass123",
            "password2": "S8rong!Pass123",
        },
    )

    assert response.status_code == 302
    user = User.objects.get(email="newweb@example.com")
    assert str(client.session["_auth_user_id"]) == str(user.pk)


@pytest.mark.django_db
def test_header_shows_account_menu_for_authenticated_customer(client):
    user = User.objects.create_user(
        email="menu@example.com",
        password="pass12345",
        mobile_number="7777777777",
    )
    client.force_login(user)

    response = client.get("/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Account" in content
    assert "My Account" in content
    assert "7777777777" in content
    assert "Saved Addresses" in content
    assert 'action="/accounts/logout/"' in content


@pytest.mark.django_db
def test_header_google_begin_uses_post_form_for_guest(client):
    response = client.get("/")

    assert response.status_code == 200
    content = response.content.decode()
    assert 'method="post" action="/auth/login/google-oauth2/?next=/"' in content
    assert 'href="/auth/login/google-oauth2/' not in content


@pytest.mark.django_db
def test_profile_page_updates_customer_details(client):
    user = User.objects.create_user(email="profile@example.com", password="pass12345")
    client.force_login(user)

    response = client.post(
        "/accounts/profile/",
        {
            "first_name": "Updated",
            "last_name": "Customer",
            "mobile_number": "9999999999",
            "date_of_birth": "1994-01-01",
            "gender": "male",
        },
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.first_name == "Updated"
    assert user.mobile_number == "9999999999"


@pytest.mark.django_db
def test_checkout_address_form_saves_and_returns_to_checkout(client):
    user = User.objects.create_user(email="address-flow@example.com", password="pass12345")
    client.force_login(user)

    response = client.post(
        "/accounts/addresses/add/",
        {
            "next": "/checkout/",
            "full_name": "Address User",
            "phone": "9999999999",
            "house": "12",
            "street": "Market Road",
            "locality": "Central",
            "city": "Delhi",
            "state": "Delhi",
            "country": "India",
            "pin_code": "110001",
            "address_type": "home",
            "default_shipping": "on",
            "default_billing": "on",
        },
    )

    address = Address.objects.get(user=user)
    assert response.status_code == 302
    assert response["Location"] == f"/checkout/?address_id={address.id}"
    assert address.default_shipping


@pytest.mark.django_db
def test_api_profile_patch_updates_customer(api_client):
    user = User.objects.create_user(email="api-profile@example.com", password="pass12345")
    api_client.force_authenticate(user)

    response = api_client.patch(
        "/api/v1/auth/profile/",
        {"first_name": "Api", "last_name": "Customer", "mobile_number": "8888888888"},
        format="json",
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "Api"
    assert user.mobile_number == "8888888888"
