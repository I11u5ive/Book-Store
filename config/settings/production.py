import os

from .base import *

DEBUG = False

# Render provides the public hostname at runtime.
render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()

if render_hostname:
    ALLOWED_HOSTS = list(dict.fromkeys(ALLOWED_HOSTS + [render_hostname]))
    CSRF_TRUSTED_ORIGINS = list(
        dict.fromkeys(CSRF_TRUSTED_ORIGINS + [f"https://{render_hostname}"])
    )

if not SECRET_KEY or SECRET_KEY == "unsafe-local-development-key-change-me":
    raise ValueError("Production SECRET_KEY must be configured.")

# WhiteNoise must be immediately after Django SecurityMiddleware.
security_middleware = "django.middleware.security.SecurityMiddleware"
whitenoise_middleware = "whitenoise.middleware.WhiteNoiseMiddleware"

if whitenoise_middleware not in MIDDLEWARE:
    MIDDLEWARE.insert(
        MIDDLEWARE.index(security_middleware) + 1,
        whitenoise_middleware,
    )

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": ("whitenoise.storage.CompressedManifestStaticFilesStorage"),
    },
}

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
