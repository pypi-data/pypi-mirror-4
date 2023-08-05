import os
import sys
import unittest
import doctest
import django

def main():
    """
    Standalone django model test with a 'memory-only-django-installation'.
    You can play with a django model without a complete django app installation.
    http://www.djangosnippets.org/snippets/1044/
    """
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings

    global_settings.SECRET_KEY = "snakeoil"
    global_settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__),
                                      'beproud', 'django', 'ssl', 'tests', 'templates'),)

    global_settings.INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.flatpages',
        'django.contrib.sites',
        'beproud.django.ssl',
    )
    global_settings.SITE_ID=1
    global_settings.ROOT_URLCONF='beproud.django.ssl.tests.urls'
    global_settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

    global_settings.SSL_URLS = (
        '^/sslurl/',
    )
    global_settings.SSL_IGNORE_URLS = (
        '^/static/',
    )

    from django.test.utils import get_runner
    test_runner = get_runner(global_settings)

    test_runner = test_runner()
    failures = test_runner.run_tests(['ssl'])
    sys.exit(failures)

if __name__ == '__main__':
    main()
