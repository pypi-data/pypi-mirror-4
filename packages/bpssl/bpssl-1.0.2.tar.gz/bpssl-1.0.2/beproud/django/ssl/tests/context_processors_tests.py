#:coding=utf-8:

from django.test import TestCase as DjangoTestCase

from beproud.django.ssl.context_processors import conf

from beproud.django.ssl.tests.base import request_factory

class ContextProcessorTestCase(DjangoTestCase):
    """
    Tests bpssl's context processors.
    """
    def test_conf(self):
        request = request_factory('get', '/')
        context = conf(request)
        self.assertEquals(context, {
            'USE_SSL': True,
            'HTTP_HOST': 'testserver',
            'SSL_HOST': 'testserver',
        })
