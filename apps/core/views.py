import urllib.parse

from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.utils.html import escapejs
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.catalog.models import Product
from .models import MobileAppBuild


def robots_txt(request):
    content = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


def latest_android_app_download(request):
    latest_build = (
        MobileAppBuild.objects.filter(platform=MobileAppBuild.Platform.ANDROID, track=MobileAppBuild.Track.TESTING, active=True)
        .exclude(build_file="")
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
    request.session["mobile_google_login_pending"] = True
    next_url = reverse("mobile-google-login-done")
    request.session["next"] = next_url
    social_url = reverse("social:begin", args=("google-oauth2",))
    csrf_token = get_token(request)
    html = f"""<!doctype html>
<html>
  <head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Continue with Google</title></head>
  <body>
    <form id="google-login" method="post" action="{social_url}?next={urllib.parse.quote(next_url)}">
      <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
      <input type="hidden" name="next" value="{next_url}">
      <noscript><button type="submit">Continue with Google</button></noscript>
    </form>
    <script>document.getElementById("google-login").submit();</script>
  </body>
</html>"""
    return HttpResponse(html)


@login_required
def mobile_google_login_done(request):
    request.session.pop("mobile_google_login_pending", None)
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


def mobile_product_open(request, slug):
    product = get_object_or_404(Product, slug=slug, status=Product.Status.ACTIVE)
    web_url = request.build_absolute_uri(product.get_absolute_url())
    app_url = f"vamikamart://product/{urllib.parse.quote(product.slug)}"
    intent_url = (
        f"intent://product/{urllib.parse.quote(product.slug)}"
        "#Intent;scheme=vamikamart;package=com.vamikamart.app;"
        f"S.browser_fallback_url={urllib.parse.quote(web_url, safe='')};end"
    )
    download_url = request.build_absolute_uri(reverse("app-download"))
    html = f"""<!doctype html>
<html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{product.name} - VamikaMart</title>
    <style>
      body {{ margin: 0; padding: 28px; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #fbfaf5; color: #17231f; }}
      .card {{ max-width: 440px; margin: 10vh auto 0; background: #fff; border: 1px solid #e7e1d2; border-radius: 16px; padding: 24px; box-shadow: 0 18px 44px rgba(31, 111, 91, .12); }}
      h1 {{ margin: 0 0 8px; font-size: 28px; }}
      p {{ color: #66716b; line-height: 1.45; }}
      a {{ display: block; text-align: center; margin-top: 12px; padding: 13px 16px; border-radius: 12px; text-decoration: none; font-weight: 850; }}
      .primary {{ background: #1f6f5b; color: #fff; }}
      .secondary {{ border: 1px solid #d8d1be; color: #17382f; }}
      .download {{ background: #0f1b22; color: #fff; }}
    </style>
  </head>
  <body>
    <main class="card">
      <h1>{product.name}</h1>
      <p>App installed hai to product VamikaMart app me open hoga. App nahi hai to latest Android app install kar sakte hain.</p>
      <a class="primary" href="{app_url}">Open in VamikaMart app</a>
      <a class="download" href="{download_url}">Install VamikaMart Android app</a>
      <a class="secondary" href="{web_url}">Continue on website</a>
    </main>
    <script>
      (function () {{
        var intentUrl = "{escapejs(intent_url)}";
        setTimeout(function () {{ window.location.href = intentUrl; }}, 250);
      }})();
    </script>
  </body>
</html>"""
    response = HttpResponse(html)
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
