class CustomerPrivacyService:
    @staticmethod
    def anonymize_user(user):
        user.email = f"deleted-user-{user.id}@example.invalid"
        user.username = f"deleted-user-{user.id}"
        user.first_name = ""
        user.last_name = ""
        user.mobile_number = ""
        user.profile_image = ""
        user.account_status = user.Status.DELETED
        user.is_active = False
        user.set_unusable_password()
        user.save()
        user.addresses.update(
            full_name="Deleted Customer",
            phone="",
            alternate_phone="",
            house="",
            street="",
            landmark="",
            locality="",
            city="",
            district="",
            state="",
            pin_code="",
        )
        return user


class VerificationService:
    @staticmethod
    def issue_email_verification(user):
        from django.utils import timezone
        from django.utils.crypto import get_random_string
        from .models import VerificationToken

        return VerificationToken.objects.create(
            user=user,
            purpose=VerificationToken.Purpose.EMAIL,
            token=get_random_string(48),
            sent_to=user.email,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )

    @staticmethod
    def issue_mobile_otp(user):
        from django.utils import timezone
        from django.utils.crypto import get_random_string
        from .models import VerificationToken

        return VerificationToken.objects.create(
            user=user,
            purpose=VerificationToken.Purpose.MOBILE,
            token=get_random_string(6, allowed_chars="0123456789"),
            sent_to=user.mobile_number,
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )

    @staticmethod
    def consume(token, purpose):
        from django.utils import timezone
        from .models import VerificationToken

        record = VerificationToken.objects.select_related("user").filter(token=token, purpose=purpose, consumed_at__isnull=True).first()
        if not record or record.expires_at < timezone.now():
            return None
        record.consumed_at = timezone.now()
        record.save(update_fields=["consumed_at"])
        if purpose == VerificationToken.Purpose.EMAIL:
            record.user.email_verified = True
            record.user.save(update_fields=["email_verified"])
        elif purpose == VerificationToken.Purpose.MOBILE:
            record.user.mobile_verified = True
            record.user.save(update_fields=["mobile_verified"])
        return record.user
