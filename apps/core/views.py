from django.http import HttpResponse
from django.shortcuts import redirect

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
