import urllib.parse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from .models import MobileAppBuild


def robots_txt(request):
    content = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


def latest_android_app_download(request):
    latest_build = (
        MobileAppBuild.objects.filter(
            active=True,
            platform=MobileAppBuild.Platform.ANDROID,
            track=MobileAppBuild.Track.TESTING,
        )
        .order_by("-version_code", "-created_at")
        .first()
    )
    if not latest_build or not latest_build.build_file:
        return HttpResponse(
            "VamikaMart Android app build is not available yet. Please upload the latest testing APK from admin.",
            status=404,
            content_type="text/plain",
        )
    return redirect(latest_build.build_file.url)


def mobile_google_login_start(request):
    redirect_uri = request.GET.get("redirect_uri") or "vamikamart://auth/google"
    if not redirect_uri.startswith("vamikamart://"):
        return HttpResponse("Invalid mobile redirect URI.", status=400, content_type="text/plain")

    request.session["mobile_google_redirect_uri"] = redirect_uri
    next_url = reverse("mobile-google-login-done")
    social_url = reverse("social:begin", args=("google-oauth2",))
    return redirect(f"{social_url}?next={urllib.parse.quote(next_url)}")


@login_required
def mobile_google_login_done(request):
    redirect_uri = request.session.pop("mobile_google_redirect_uri", "vamikamart://auth/google")
    refresh = RefreshToken.for_user(request.user)
    query = urllib.parse.urlencode(
        {
            "status": "success",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    )
    separator = "&" if "?" in redirect_uri else "?"
    return redirect(f"{redirect_uri}{separator}{query}")
