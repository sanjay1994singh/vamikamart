import urllib.parse

from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.utils.html import escapejs
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from .models import MobileAppBuild


def robots_txt(request):
    content = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


def latest_android_app_download(request):
    latest_build = (
        MobileAppBuild.objects.filter(platform=MobileAppBuild.Platform.ANDROID, track=MobileAppBuild.Track.TESTING)
        .order_by("-version_code", "-created_at", "-id")
        .first()
    )
    if not latest_build or not latest_build.build_file:
        return HttpResponse(
            "VamikaMart Android app build is not available yet. Please upload the latest testing APK from admin.",
            status=404,
            content_type="text/plain",
        )
    separator = "&" if "?" in latest_build.build_file.url else "?"
    response = HttpResponseRedirect(f"{latest_build.build_file.url}{separator}v={latest_build.version_code}")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response


def mobile_google_login_start(request):
    redirect_uri = request.GET.get("redirect_uri") or "vamikamart://auth/google"
    if not redirect_uri.startswith("vamikamart://"):
        return HttpResponse("Invalid mobile redirect URI.", status=400, content_type="text/plain")

    request.session["mobile_google_redirect_uri"] = redirect_uri
    next_url = reverse("mobile-google-login-done")
    social_url = reverse("social:begin", args=("google-oauth2",))
    csrf_token = get_token(request)
    html = f"""<!doctype html>
<html>
  <head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Continue with Google</title></head>
  <body>
    <form id="google-login" method="post" action="{social_url}?next={urllib.parse.quote(next_url)}">
      <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
      <noscript><button type="submit">Continue with Google</button></noscript>
    </form>
    <script>document.getElementById("google-login").submit();</script>
  </body>
</html>"""
    return HttpResponse(html)


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
    deep_link = f"{redirect_uri}{separator}{query}"
    parsed_deep_link = urllib.parse.urlparse(deep_link)
    intent_path = f"{parsed_deep_link.netloc}{parsed_deep_link.path}"
    if parsed_deep_link.query:
        intent_path = f"{intent_path}?{parsed_deep_link.query}"
    intent_link = f"intent://{intent_path}#Intent;scheme={parsed_deep_link.scheme};package=com.vamikamart.app;end"
    js_deep_link = escapejs(deep_link)
    js_intent_link = escapejs(intent_link)
    html = f"""<!doctype html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Opening VamikaMart</title>
    <style>
      body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; padding: 32px; color: #1d2521; background: #fbfaf5; }}
      .panel {{ max-width: 420px; margin: 18vh auto 0; background: #fff; border: 1px solid #e7e1d2; border-radius: 14px; padding: 24px; text-align: center; }}
      a {{ display: inline-block; margin-top: 14px; padding: 12px 18px; border-radius: 10px; background: #1f6f5b; color: #fff; text-decoration: none; font-weight: 800; }}
      p {{ color: #66716b; }}
    </style>
  </head>
  <body>
    <div class="panel">
      <h1>Opening VamikaMart</h1>
      <p>Google login complete ho gaya. App automatically open ho rahi hai.</p>
      <a id="open-app" href="{deep_link}">Open VamikaMart app</a>
    </div>
    <script>
      (function () {{
        var appUrl = "{js_deep_link}";
        var intentUrl = "{js_intent_link}";
        var opened = false;
        function openApp() {{
          if (opened) return;
          opened = true;
          window.location.href = appUrl;
          setTimeout(function () {{ window.location.href = intentUrl; }}, 700);
          setTimeout(function () {{ window.close(); }}, 1800);
        }}
        document.getElementById("open-app").addEventListener("click", function (event) {{
          event.preventDefault();
          opened = false;
          openApp();
        }});
        openApp();
      }})();
    </script>
  </body>
</html>"""
    response = HttpResponse(html)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
