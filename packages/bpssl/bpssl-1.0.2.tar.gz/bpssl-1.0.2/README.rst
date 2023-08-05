================
bpssl
================

bpssl is a Django application that helps you support
HTTPS on your website. The main functionality is performing redirection
for HTTPS only URLs and views. For instance, if a request for your
login view '/login' is recieved over HTTP, the provided middleware can
redirect the user to the equivalent HTTPS page.

Specifying views and urls as secure is supported as are `flatpages`_. `Fastcgi`_
and HTTP proxy setups are also well supported. See the documentation at:

* English: http://beproud.bitbucket.org/bpssl-1.0.2/en/
* 日本語: http://beproud.bitbucket.org/bpssl-1.0.2/ja/

bpssl draws inspiration from the well known SSL Middleware snippets on
djangosnippets.org. It roughly supports the features of the following
snippets:

* http://djangosnippets.org/snippets/880/
* http://djangosnippets.org/snippets/240/
* http://djangosnippets.org/snippets/1999/

Please file bugs at: http://bitbucket.org/beproud/bpssl/issues/

Middleware
=====================

bpssl provides an ``SSLRedirectMiddleware`` which can redirect users from
secure pages to non-secure pages and visa-versa. Urls are set up by adding
regular expressions to the ``SSL_URLS`` setting in settings.py.
``SSLRedirectMiddleware`` can also be extended to support more specific use
cases.

ssl_view decorator
=====================

bpssl provides an ``ssl_view()`` decorator which can be used instead of the
``SSL_URLS`` to specify that a particular view should be secure.

.. _flatpages: http://docs.djangoproject.com/en/dev/ref/contrib/flatpages/
.. _Fastcgi: http://docs.djangoproject.com/en/dev/howto/deployment/fastcgi

Development
=====================

Generally you will want to develop bpssl in a virtualenv with pip::

    $ mkvirtualenv bpssl

You can install the requirements using the requirements.txt and pip::
    
    $ pip install -r setup/requirements.txt

And run tests normally using setup.py::

    $ python setup.py test 
