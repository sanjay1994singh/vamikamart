from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView
from .forms import AddressForm, CustomerRegistrationForm, ProfileUpdateForm
from .models import Address


class RegisterView(CreateView):
    template_name = "accounts/register.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend="django.contrib.auth.backends.ModelBackend")
        return response


class AccountPasswordChangeView(PasswordChangeView):
    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("home")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = ProfileUpdateForm(instance=self.request.user)
        context["address_form"] = AddressForm(initial={
            "full_name": self.request.user.get_full_name() or self.request.user.email,
            "phone": self.request.user.mobile_number,
            "country": "India",
            "default_shipping": not self.request.user.addresses.exists(),
            "default_billing": not self.request.user.addresses.exists(),
        })
        context["addresses"] = self.request.user.addresses.order_by("-default_shipping", "-created_at")
        return context

    def post(self, request, *args, **kwargs):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
        context = self.get_context_data(**kwargs)
        context["profile_form"] = form
        return self.render_to_response(context)


class AddressCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = AddressForm(request.POST)
        next_url = request.POST.get("next") or request.GET.get("next") or reverse("profile")
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Delivery address saved.")
            return redirect(f"{next_url}?address_id={address.id}")
        messages.error(request, "Please check the delivery address form.")
        return redirect(next_url)


class AddressDefaultView(LoginRequiredMixin, View):
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.default_shipping = True
        address.default_billing = True
        address.save(update_fields=["default_shipping", "default_billing"])
        messages.success(request, "Default delivery address updated.")
        return redirect(request.POST.get("next") or request.GET.get("next") or "profile")
