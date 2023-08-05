===================================
Limiting access to secure requests
===================================

Limiting Access via URLs
-----------------------------------

One way to specify which requests should be treated as secure is to identify them
by url. This way setting entire sets of urls to be secure is easy and maintenance
is fairly painless.

For instance one might want to set all of a user's account information to be
accessed via secure requests so you could set all urls under ``/accounts/`` to
be secure urls. The same might apply for making payments under ``/payment`` or
some other such scheme.

Using the SSLRedirectMiddleware
+++++++++++++++++++++++++++++++++++

.. class:: beproud.django.ssl.middleware.SSLRedirectMiddleware

Using the
:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
you can add secure request redirection over your whole site.

:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
uses a setting called :ref:`SSL_URLS <setting-ssl-urls>` to determine which urls will
be accessed via SSL (HTTPS). You set this setting the in your
``settings.py``.  :ref:`SSL_URLS <setting-ssl-urls>` is a list of regular expressions
that are checked against the request url as it is found in `request.path_info`_.
If one of the regular expressions matches then the URL is treated as a secure url 
and non-secure accesses are redirected to the secure url. For instance, using the
setup below if a request is recieved for the url ``http://www.example.com/login/``,
the user will be redirected to ``https://www.example.com/login/`` because the url
matches a the :ref:`SSL_URLS <setting-ssl-urls>` settings. The paths matched against
the regular expression are different from ``urls.py`` in that they start with a '/'
so keep that in mind.

.. code-block:: python

    SSL_URLS = (
        '^/login/',
        '^/purchase/'
        # ...
    )

In case there are some urls you want to be accessable via HTTP or HTTPS, you
can set those in the :ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>` setting. For
instance, static files served by your application or i18n javascript would typically
be accessable via both HTTP and HTTPS. :ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>`
is defined exactly like :ref:`SSL_URLS <setting-ssl-urls>`.

.. code-block:: python

    SSL_IGNORE_URLS = (
        '^/i18n_js$',
        '^/static/',
        # ...
    )

:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>` does the following:

* If the request url matches a url in :ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>` then do nothing.
* If the request url matches a url in :ref:`SSL_URLS <setting-ssl-urls>` and the request is not-secure then the user is redirected to the secure version of the page. 
* If the request url does not match a url in :ref:`SSL_URLS <setting-ssl-urls>` and the request is secure then the user is redirected to the non-secure version of the page. 

.. note:: 

    Secure requests to non-secure pages are redirected to the non-secure url because
    pages that can be accessed via multiple urls can confuse search engines and is
    not particularly `RESTful`_.

Limiting Access to Views
-----------------------------------

One might also want to limit access to particular views because they encapsulate
some kind of functionality that should be accessed in a secure way. Multiple
urls could be accessing this view so it may not make sense to maintain the
security settings as URLs.

The RAW Way
+++++++++++++++++++++++++++++++++++

Because some urls may change or multiple urls could be handled by the same view,
you may want to limit access to secure requests at the view level. The simple raw
way to limit access to pages to secure requests is to check `request.is_secure()`_
to see if the request is secure::

    from django.http import HttpResponseRedirect
    from django.http import get_host

    def my_secure_view(request):
        if request.is_secure():
            return HttpResponseRedirect("https://%s%s" % (get_host(request), request.get_full_path()))
        # ...

However, by limiting access this way the :class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>` has no way of
knowing that the page is secure and thus may conflict with your view unless you
add the URL to :ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>`.

The ssl_view decorator
+++++++++++++++++++++++++++++++++++

.. function:: beproud.django.ssl.decorators.ssl_view 

As a shortcut the ``ssl_view()`` decorator is provided to indicate that your view
should be restricted to secure requests. Example::

    from beproud.django.ssl.decorators import ssl_view 

    @ssl_view
    def my_secure_view(request):
        ...

``ssl_view()`` implements the same functionality as the
:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
but works without having to set the URL in :ref:`SSL_URLS <setting-ssl-urls>`.
:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
will also recognize views using the ``ssl_view()`` decorator and won't conflict with
your view.

Using an HTTP Reverse Proxy
-----------------------------------

.. class:: beproud.django.ssl.middleware.SSLProxyMiddleware 

:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>`
will update the request object to make sure that
`request.is_secure()`_ returns true when processing a secure request from a properly
set up HTTP reverse proxy server. See
:ref:`Web Server Setup <install-web-server-setup>` for more info on how to set up
reverse proxy web servers to work with
:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>`.

You will need to set the :ref:`SSL_REQUEST_HEADER <setting-ssl-request-header>`
setting to the name and value of the header you use to pass whether a request
is secure or not. The default value of this setting is shown below:

.. code-block:: python

    SSL_REQUEST_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>` does the following:

* If the name and value of the HTTP header defined by :ref:`SSL_REQUEST_HEADER <setting-ssl-request-header>` equals the value 
  of the header sent with the request then set `request.is_secure()`_ to return True.

.. note::

    :class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>` should be set as early as possible in your `MIDDLEWARE_CLASSES`_ setting so that
    any middleware which looks at `request.is_secure()`_ will get the right value. At the very least it should be before your
    :class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`.

.. _`request.path_info`: http://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.path_info
.. _`request.is_secure()`: http://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.is_secure
.. _`RESTful`: http://en.wikipedia.org/wiki/Representational_State_Transfer
.. _`MIDDLEWARE_CLASSES`: http://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
