import pytest
from apps.accounts.models import User
from apps.accounts.services import CustomerPrivacyService


@pytest.mark.django_db
def test_customer_anonymization_preserves_user_row():
    user = User.objects.create_user(email="person@example.com", username="person", password="pass12345", mobile_number="999")
    CustomerPrivacyService.anonymize_user(user)
    user.refresh_from_db()
    assert user.account_status == User.Status.DELETED
    assert not user.is_active
    assert "deleted-user" in user.email
