from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


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
