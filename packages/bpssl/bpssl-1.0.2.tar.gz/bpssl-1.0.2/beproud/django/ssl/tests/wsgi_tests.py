#:coding=utf-8:

import os
from urlparse import urlsplit, urlunsplit

from django.test import TestCase as DjangoTestCase

from beproud.django.ssl.tests.base import (
    BaseTestCase, SSLRedirectTests, SSLDecoratorTests,
    UseSSLTests, FlatpageTests,
)

class WSGITestCase(BaseTestCase):
    def request(self, path, method='GET', https=False, headers={}):
        if https or urlsplit(path)[0] == 'https':
            headers = headers.copy()
            headers.update({'wsgi.url_scheme': 'https'})
        return super(WSGITestCase, self).request(path, method, https, headers)

class WSGISSLRedirectTestCase(SSLRedirectTests, WSGITestCase, DjangoTestCase):
    pass
class WSGISSLDecoratorTestCase(SSLDecoratorTests, WSGITestCase, DjangoTestCase):
    pass
class WSGIUseSSLTestCase(UseSSLTests, WSGITestCase, DjangoTestCase):
    pass
class WSGIFlatpageTestCase(FlatpageTests, WSGITestCase, DjangoTestCase):
    pass
