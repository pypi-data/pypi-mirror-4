#:coding=utf-8:

from urlparse import urlsplit, urlunsplit

from django.test import TestCase as DjangoTestCase

from beproud.django.ssl.tests.base import (
    BaseTestCase, SSLRedirectTests, SSLDecoratorTests,
    UseSSLTests, FlatpageTests
)

class ProxyTestCase(BaseTestCase):
    SSL_REQUEST_HEADER = ('HTTP_X_FORWARDED_SSL', 'on')
    MIDDLEWARE_CLASSES = (
        'beproud.django.ssl.middleware.SSLProxyMiddleware',
        'beproud.django.ssl.middleware.SSLRedirectMiddleware',
    )

    def request(self, path, method='GET', https=False, headers={}):
        if https or urlsplit(path)[0] == 'https':
            headers = headers.copy()
            headers.update({'HTTP_X_FORWARDED_SSL': 'ON'})
        return super(ProxyTestCase, self).request(path, method, https, headers)

class ProxySSLRedirectTestCase(SSLRedirectTests, ProxyTestCase, DjangoTestCase):
    pass
class ProxySSLDecoratorTestCase(SSLDecoratorTests, ProxyTestCase, DjangoTestCase):
    pass
class ProxyUseSSLTestCase(UseSSLTests, ProxyTestCase, DjangoTestCase):
    pass
class ProxyFlatpageTestCase(FlatpageTests, ProxyTestCase, DjangoTestCase):
    pass

class ProxyProtocolTestCase(BaseTestCase):
    SSL_REQUEST_HEADER = ('HTTP_X_PROXY_REQUEST_PROTOCOL', 'https')
    MIDDLEWARE_CLASSES = (
        'beproud.django.ssl.middleware.SSLProxyMiddleware',
        'beproud.django.ssl.middleware.SSLRedirectMiddleware',
    )

    def request(self, path, method='GET', https=False, headers={}):
        if https or urlsplit(path)[0] == 'https':
            headers = headers.copy()
            headers.update({'HTTP_X_PROXY_REQUEST_PROTOCOL': 'HTTPS'})
        return super(ProxyProtocolTestCase, self).request(path, method, https, headers)

class ProxyProtocolSSLRedirectTestCase(SSLRedirectTests, ProxyProtocolTestCase, DjangoTestCase):
    pass
class ProxyProtocolSSLDecoratorTestCase(SSLDecoratorTests, ProxyProtocolTestCase, DjangoTestCase):
    pass
class ProxyProtocolUseSSLTestCase(UseSSLTests, ProxyProtocolTestCase, DjangoTestCase):
    pass
class ProxyProtocolFlatpageTestCase(FlatpageTests, ProxyProtocolTestCase, DjangoTestCase):
    pass
