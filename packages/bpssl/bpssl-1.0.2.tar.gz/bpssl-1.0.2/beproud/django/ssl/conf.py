#:coding=utf-8:

from django.conf import settings as django_settings

settings = type('Settings', (object,), {})()

settings.USE_SSL = getattr(django_settings, "USE_SSL", True)
settings.SSL_URLS = getattr(django_settings, "SSL_URLS", ())
settings.SSL_IGNORE_URLS = getattr(django_settings, "SSL_IGNORE_URLS", ())
settings.SSL_REQUEST_HEADER = getattr(
    django_settings, "SSL_REQUEST_HEADER",
    ('HTTP_X_FORWARDED_PROTOCOL', 'https')
)
