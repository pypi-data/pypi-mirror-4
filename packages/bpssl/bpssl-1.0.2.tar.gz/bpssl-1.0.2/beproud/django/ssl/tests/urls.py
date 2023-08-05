#:coding=utf-8:
from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

from beproud.django.ssl.decorators import ssl_view

urlpatterns = patterns('',
    (r'sslurl/someurl', lambda request: HttpResponse("Spam and Eggs")),
    (r'some/other/url', lambda request: HttpResponse("Spam and Eggs")),
    (r'decorated/ssl/view', ssl_view(lambda request: HttpResponse("Spam and Eggs"))),
    # Test decorating multiple times
    (r'decorated/ssl/view', never_cache(ssl_view(lambda request: HttpResponse("Spam and Eggs")))),
)
