===================================
Installation
===================================

Application Install
-----------------------------

Installing bpssl is easy, but there are some non-obvious
steps for setting up your web server that you will need to do to get
it working.

First install the ``bpssl`` package using PIP::

    $ pip install bpssl

or easy_install::

    $ easy_install bpssl

Next add ``'beproud.django.ssl'`` to your `INSTALLED_APPS`_ in your ``settings.py``.

.. code-block:: python 

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        # ...
        'beproud.django.ssl',
        # ...
    )

Context Processor Setup
-----------------------------

.. function:: beproud.django.ssl.context_processors.conf

Add the :func:`beproud.django.ssl.context_processors.conf` context processor to
your `TEMPLATE_CONTEXT_PROCESSORS`_ setting.

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        #...
        'beproud.django.ssl.context_processors.conf',
        #...
    )

Middleware Setup
-----------------------------

Add ``'beproud.django.ssl.middleware.SSLRedirectMiddleware'`` to your `MIDDLEWARE_CLASSES`_ setting. 

.. code-block:: python 

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        # ...
        'beproud.django.ssl.middleware.SSLRedirectMiddleware',
        # ...
    )

If using a HTTP proxy you will need to add
``'beproud.django.ssl.middleware.SSLProxyMiddleware'`` to `MIDDLEWARE_CLASSES`_.
``SSLProxyMiddleware`` should be added as early as possible in your `MIDDLEWARE_CLASSES`_
setting.

.. code-block:: python 

    MIDDLEWARE_CLASSES = (
        'beproud.django.ssl.middleware.SSLProxyMiddleware',
        # ...
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        # ...
        'beproud.django.ssl.middleware.SSLRedirectMiddleware',
        # ...
    )

.. _install-web-server-setup:

Web Server Setup
----------------------------

Because SSL decoding and encoding is done by the web server, it's impossible for a
Django application to know whether a request is secure or not unless the web server
tells it. In order to pass that information to the Django application some setup on
the webserver is usually necessary. In particular because ``beproud.django.ssl``
relies on the `request.is_secure()`_ method we need to get `request.is_secure()`_
to return the right results.

nginx/FastCGI
+++++++++++++++++++++++++++++

When using nginx and FastCGI it's sufficient to set the information in a
``fastcgi_param``. Setting the fastcgi parameter ``HTTPS`` to ``on`` will tell the
flup server that the request is a secure request. Flup will then wrap the request
accordingly, setting the ``wsgi.url_scheme`` to ``https`` and making
`request.is_secure()`_ return the correct value.

.. code-block:: nginx 

    location / {
        include                 /etc/nginx/fastcgi_params;
        fastcgi_pass            upstream;
        fastcgi_param           HTTPS on;
    }

nginx/HTTP proxy
+++++++++++++++++++++++++++++

When using nginx as a HTTP reverse proxy you will need to pass information about
whether a request is secure or not in an HTTP header. In order to avoid falling
victim to man in the middle attacks where an attacker could cause data that
should be sent over a secure channel to be sent over an unsecure
channel, nginx will need to set or strip this header for non-secure requests.

Set the name and value of the header to the value you set in the 
:ref:`SSL_REQUEST_HEADER <setting-ssl-request-header>` setting in order to use it
in conjunction with the
:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>`.

.. code-block:: nginx

    #HTTP
    server {
        listen 80;
        location / {
            proxy_pass          http://myproxy;    
            
            # We need to set this header for HTTP requests as well
            # so that we won't fall victim to man-in-the-middle attacks.
            proxy_set_header X_FORWARDED_PROTOCOL      "http";
            # ...
        }
    }
     
    # HTTPS
    server {
        listen 443;
        ssl on;
        # ...
        location / {
            proxy_pass          http://myproxy;    
            # This should be set to the same headeras the
            # non-ssl setup above.
            proxy_set_header    X_FORWARDED_PROTOCOL   https; 
            # ...
        }
    }

.. Apache・HTTP proxy
.. +++++++++++++++++++++++++++++
.. 
.. TODO

Apache/FastCGI
+++++++++++++++++++++++++++++

With Apache/FastCGI you can setting the HTTPS environment variable should be sufficient to
get `request.is_secure()`_ to work in a FastCGI environment. You can add the environment
variable to FastCGI using the Apache rewrite module like so:

.. code-block:: apache

    <VirtualHost *:443>
        SSLEngine on
        # ...

        RewriteEngine on
        RewriteCond %{HTTPS} on
        RewriteRule .* - [E=HTTPS:on]

        # ...
    </VirtualHost>

Apache/mod_wsgi
+++++++++++++++++++++++++++++

In an Apache/mod_wsgi setup where HTTPS is handled by the same server, mod_wsgi will
set the ``wsgi.url_scheme`` environment variable appropriately and
`request.is_secure()`_ should return the correct value without any special setup.

.. _`request.is_secure()`: http://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.is_secure
.. _`INSTALLED_APPS`: http://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
.. _`MIDDLEWARE_CLASSES`: http://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
.. _`TEMPLATE_CONTEXT_PROCESSORS`: http://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
