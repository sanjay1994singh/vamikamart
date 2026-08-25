from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["127.0.0.1", "localhost", "vamikamart.testonline.tech"],
)


def _csrf_origins_from_hosts(hosts):
    origins = []
    for host in hosts:
        normalized = host.strip()
        if not normalized or normalized in {"*", "127.0.0.1", "localhost"}:
            continue
        origins.extend([f"https://{normalized}", f"http://{normalized}"])
    return origins


CSRF_TRUSTED_ORIGINS = sorted(set(
    env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
    + _csrf_origins_from_hosts(ALLOWED_HOSTS)
))
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
)
