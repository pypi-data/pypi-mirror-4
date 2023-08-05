===================================
インストール
===================================

アプリケーションインストール
-----------------------------

bpssl をインストールするのが簡単ですが、ウェブサーバーと
連携するところがありますので、注意しないといけません。

まずは、ポッケージを PIP でインストールします::

    $ pip install bpssl

もしくは ``easy_install`` で::

    $ easy_install bpssl

次に、 ``'beproud.django.ssl'`` を ``settings.py`` の `INSTALLED_APPS`_ に追加してください。

.. code-block:: python 

    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        #...
        'beproud.django.ssl',
        #...
    )

コンテキストプロセッサー
-----------------------------

.. function:: beproud.django.ssl.context_processors.conf

:func:`beproud.django.ssl.context_processors.conf` コンテキストプロセッサーを
`TEMPLATE_CONTEXT_PROCESSORS`_ に追加してください。

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = (
        #...
        'beproud.django.ssl.context_processors.conf',
        #...
    )

ミドルウエアを設定
-----------------------------

それから、 ``'beproud.django.ssl.middleware.SSLRedirectMiddleware'`` を `MIDDLEWARE_CLASSES`_ に追加してください。

.. code-block:: python 

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        #...
        'beproud.django.ssl.middleware.SSLRedirectMiddleware',
        #...
    )

HTTPのリバースプロクシーを使う場合は、 
``'beproud.django.ssl.middleware.SSLProxyMiddleware'`` を `MIDDLEWARE_CLASSES`_ に
追加する必要があります。できるだけ上に登録すること。

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

ウェブサーバーの設定
----------------------------

SSLのエンコードやデコードがウェブサーバーで行うため、Djangoのアプリケーション側で、
リクエストがセキュアかどうかを判断するには、ウェブサーバーからその情報
をアップストリームのアプリケーションサーバーに送る必要があります。その情報を送る
ために、ウェブサーバーを設定する必要があります。具体的にいうと、 `request.is_secure()`_
に頼っているので、このメソッドが正しい値を返すようにします。

nginx・FastCGIの場合
+++++++++++++++++++++++++++++

nginxとFastCGIを使う場合、ウェブサーバーの設定で、FastCGIの ``HTTPS`` パラメーターを
``on`` に設定すれば、 Django のアプリケーションはHTTPかHTTPSかを判断することが
できます。そうするには、 ``fastcgi_param`` を ``HTTPS on`` に設定します。
``HTTPS`` を ``'on'`` に設定すれば、flup は ``wsgi.url_scheme`` を ``https`` に設定し、
`request.is_secure()`_ が正しい値を返すようになります。

.. code-block:: nginx

    location / {
        include                 /etc/nginx/fastcgi_params;
        fastcgi_pass            upstream;
        fastcgi_param           HTTPS on;
    }

nginx・HTTP proxyの場合
+++++++++++++++++++++++++++++

HTTPリバースプロクシーとして、nginx を使う場合、HTTPリクエストがセキュアか
どうかの情報をHTTPヘッダーでアプリケーションに渡す必要があります。
HTTPSで、送っているはずなのに、ブラウザがHTTPで情報を送らせてしまう
man-in-the-middle 攻撃を避けるために、 HTTP リクエストの場合でも、nginxで
このヘッダーを設定する、もしくは削る必要があります。

:ref:`SSL_REQUEST_HEADER <setting-ssl-request-header>` で設定したヘッダー名と
値を nginx 側で設定してください。
:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>`
と併用します。

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

.. Apache・HTTP proxyの場合
.. +++++++++++++++++++++++++++++
.. 
.. TODO

Apache・FastCGIの場合
+++++++++++++++++++++++++++++

Apache・FastCGIの場合は、HTTPS の環境変数を設定したら、 `request.is_secure()`_ は
正しく動作するはず。Apache の rewrite モジュールで、以下の様に HTTPS 環境変数を
設定できます。

.. code-block:: apache

    <VirtualHost *:443>
        SSLEngine on
        # ...

        RewriteEngine on
        RewriteCond %{HTTPS} on
        RewriteRule .* - [E=HTTPS:on]

        # ...
    </VirtualHost>

Apache・mod_wsgiの場合
+++++++++++++++++++++++++++++

Apache・mod_wsgi を使う場合は、 ``wsgi.url_scheme`` が設定していますので、
特に特別な設定をせずに、 `request.is_secure()`_ が正しい値を返します。

.. _`request.is_secure()`: http://djangoproject.jp/doc/ja/1.0/ref/request-response.html#django.http.HttpRequest.is_secure
.. _`INSTALLED_APPS`: http://djangoproject.jp/doc/ja/1.0/ref/settings.html#installed-apps
.. _`MIDDLEWARE_CLASSES`: http://djangoproject.jp/doc/ja/1.0/ref/settings.html#setting-MIDDLEWARE_CLASSES 
.. _`TEMPLATE_CONTEXT_PROCESSORS`: http://djangoproject.jp/doc/ja/1.0/ref/settings.html#template-context-processors
