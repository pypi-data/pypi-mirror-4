#:coding=utf-8:

from django.conf import settings as django_settings
from beproud.django.ssl.conf import settings

__all__ = ('conf',)

def conf(request):
    return {
        'USE_SSL': settings.USE_SSL,
        'HTTP_HOST': getattr(django_settings, 'HTTP_HOST', request.get_host()),
        'SSL_HOST': getattr(django_settings, 'SSL_HOST', request.get_host()),
    }
