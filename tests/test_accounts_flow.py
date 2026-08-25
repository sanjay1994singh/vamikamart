import pytest

from apps.accounts.models import Address, User


@pytest.mark.django_db
def test_user_manager_normalizes_email_and_generates_username():
    user = User.objects.create_user(email="Buyer@Example.COM", password="pass12345")

    assert user.email == "Buyer@example.com"
    assert user.username == "Buyer"
    assert user.check_password("pass12345")


@pytest.mark.django_db
def test_generated_usernames_do_not_collide_for_same_email_prefix():
    first = User.objects.create_user(email="buyer@example.com", password="pass12345")
    second = User.objects.create_user(email="buyer@example.org", password="pass12345")

    assert first.username == "buyer"
    assert second.username == "buyer2"


@pytest.mark.django_db
def test_default_shipping_address_is_unique_per_customer():
    user = User.objects.create_user(email="address@example.com", password="pass12345")
    first = Address.objects.create(
        user=user,
        full_name="First",
        phone="1",
        house="1",
        street="Street",
        locality="Locality",
        city="Delhi",
        state="Delhi",
        pin_code="110001",
        default_shipping=True,
    )
    second = Address.objects.create(
        user=user,
        full_name="Second",
        phone="2",
        house="2",
        street="Street",
        locality="Locality",
        city="Delhi",
        state="Delhi",
        pin_code="110001",
        default_shipping=True,
    )

    first.refresh_from_db()
    second.refresh_from_db()
    assert not first.default_shipping
    assert second.default_shipping
