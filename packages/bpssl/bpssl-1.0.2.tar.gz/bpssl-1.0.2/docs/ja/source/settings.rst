:mod:`settings` -- bpssl 設定 
================================================================

.. _setting-ssl-urls:

SSL_URLS
---------------------

SSL専用URLの正規表現のリストです。リクエストのURLがいずれかの正規表現にマッチしたら、
:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
はそのURLをSSLのリクエストでしかアクセスできないようにする。HTTPでアクセスが来た場合、
HTTPSのほうのURLにリダイレクトする。

.. code-block:: python

    SSL_URLS = (
        '^/login/',
        '^/purchase/'
        #...
    )

.. _setting-ssl-ignore-urls:

SSL_IGNORE_URLS
---------------------

HTTPS でも、HTTP でも、アクセスしても大丈夫ようなURLがあれば、
:ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>` に追加します。 例:
静的ファイル、ユーザーメディア等。

.. code-block:: python

    SSL_IGNORE_URLS = (
        '^/static/',
        #...
    )

.. _setting-ssl-host:

SSL_HOST
---------------------

SSLのドメインがHTTPのドメインと違う場合、 :ref:`SSL_HOST <setting-ssl-host>`
を設定します。 :ref:`SSL_HOST <setting-ssl-host>` は設定されてない場合、
リクエストのドメインを使います。

.. code-block:: python

    SSL_HOST = 'secure.example.com'

.. _setting-http-host:

HTTP_HOST
---------------------

HTTP アクセスのドメインが HTTPS のドメインと違う場合、 
:ref:`HTTP_HOST <setting-http-host>` を設定します。
:ref:`HTTP_HOST <setting-http-host>` は設定されてない場合、
リクエストのドメインを使います。

.. code-block:: python

    HTTP_HOST = 'example.com'

.. _setting-ssl-request-header:

SSL_REQUEST_HEADER
---------------------

:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>`
を使う場合、リバースプロクシウェブサーバーから来たリクエストがセキュアかどうか
を指定するヘッダーの名前と値を２タップル（長さが２のタップル）として
設定します。 ``('HTTP_X_FORWARDED_SSL', 'on')`` や、
``('HTTP_X_FORWARDED_PROTOCOL', 'https')`` がやくある例となります。

:ref:`SSL_REQUEST_HEADER <setting-ssl-request-header>` のデフォールト値は以下
になります。

.. code-block:: python

    SSL_REQUEST_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
