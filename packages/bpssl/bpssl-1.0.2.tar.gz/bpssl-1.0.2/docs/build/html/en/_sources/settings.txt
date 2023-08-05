Settings
================================================================

.. module:: beproud.django.ssl.conf
   :synopsis: Settings 
.. moduleauthor:: Ian Lewis <ian@beproud.jp>
.. currentmodule:: beproud.django.ssl.conf

.. _setting-ssl-urls:

SSL_URLS
---------------------

:ref:`SSL_URLS <setting-ssl-urls>` is a list of regular expressions that are matched against the request url
by :class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
to determine if a request should be processed or redirected to a secure or non-secure
url. See 
:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
for an explanation of how :ref:`SSL_URLS <setting-ssl-urls>` are used.

.. code-block:: python

    SSL_URLS = (
        '^/login/',
        '^/purchase/'
        ...
    )

.. _setting-ssl-ignore-urls:

SSL_IGNORE_URLS
---------------------

``SSL_IGNORE_URLS`` are urls that can be accessed by secure as well as non-secure
requests.

.. code-block:: python

    SSL_IGNORE_URLS = (
        '^/static/',
        ...
    )

.. _setting-ssl-host:

SSL_HOST
---------------------

Sometimes websites serve secure pages via a seperate domain such as
``secure.example.com`` to further express that the page that the user is visiting
is secure.

``SSL_HOST`` sets the domain of the ssl host. When redirecting to ssl urls 
``beproud.django.ssl`` will redirect to this host. The default is to redirect
to the same host as the non-secure request.

.. code-block:: python

    SSL_HOST = 'secure.example.com'

.. _setting-http-host:

HTTP_HOST
---------------------

``HTTP_HOST`` sets the domain of the non-secure host. When redirecting
non-secure urls ``beproud.django.ssl`` will redirect to this host. The default
is to redirect to the same host as the secure request.  So when ``SSL_HOST``
is set you will almost always want to set this setting as well.

.. code-block:: python

    HTTP_HOST = 'example.com'

.. _setting-ssl-request-header:

SSL_REQUEST_HEADER
---------------------

When using the :class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>`, 
``SSL_REQUEST_HEADER`` should be set to the name and value of the HTTP header, in the form of a two
tuple, that is forwarded from the reverse proxy server for secure requests.

Typical settings for the ``SSL_REQUEST_HEADER`` setting would be
('HTTP_X_FORWARDED_SSL', 'on') or ('HTTP_X_FORWARDED_PROTOCOL', 'https')

The default value for ``SSL_REQUEST_HEADER`` is shown below.

.. code-block:: python

    SSL_REQUEST_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
