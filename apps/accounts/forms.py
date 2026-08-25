from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Address, User


class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "mobile_number")

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "mobile_number", "date_of_birth", "gender")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
            "full_name",
            "phone",
            "alternate_phone",
            "house",
            "street",
            "landmark",
            "locality",
            "city",
            "district",
            "state",
            "country",
            "pin_code",
            "address_type",
            "default_shipping",
            "default_billing",
        )
