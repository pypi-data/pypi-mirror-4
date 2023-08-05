==================================================================
セキュアリクエストでしかアクセスできないように制限をかける
==================================================================

URLでアクセスを制限する
-----------------------------------

セキュアURLにアクセスを制限する方法の一つは、URLでアクセスを制限することです。
こと方法で、一部のURLでアクセスを制限することができます。

例えば、ユーザーアカウント関連ページを全部 HTTPS で制限したい場合は、
``/accounts/`` で始まるURLを制限することができます。同じく、購入や、決済
の ``/payment/`` で始まるURLを制限することができます。

SSLRedirectMiddleware を利用
+++++++++++++++++++++++++++++++++++

.. class:: beproud.django.ssl.middleware.SSLRedirectMiddleware

``SSLRedirectMiddleware`` を利用すれば、全サイトにセキュアリクエストの制限をかけることができます。

``SSLRedirectMiddleware`` で :ref:`SSL_URLS <setting-ssl-urls>` という設定を利用し、
ある URL は SSL でアクセスするかどうかが決まります。 :ref:`SSL_URLS <setting-ssl-urls>`
を ``settings.py`` に設定します。 :ref:`SSL_URLS <setting-ssl-urls>` は `request.path_info`_ で定義されている URL にマッチする正規表現のリストになります。 いずれかの正規表現がと
マッチした場合、その URL はセキュアURLとして処理します。 例えば、以下の設定によって、
``http://www.example.com/login/`` という URL でアクセスが来た場合、
:ref:`SSL_URLS <setting-ssl-urls>` の正規表現にマッチしたため、 ユーザーは
``https://www.example.com/login/`` にリダイレクトされます。正規表現にマッチする
URL は ``urls.py`` と違って、 '/' 文字から始まりますので、ご注意ください。

.. code-block:: python

    SSL_URLS = (
        '^/login/',
        '^/purchase/'
        # ...
    )

HTTP でも、 HTTPSでも、アクセスできるようにしたい場合は、 
:ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>` に設定できます。例えば、
静的ファイルや、国際化 javascript は HTTP でも、HTTPSでも、
アクセスする必要がある場合が多い。 :ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>`
の書き方は :ref:`SSL_URLS <setting-ssl-urls>` の書き方と一緒です。

.. code-block:: python

    SSL_IGNORE_URLS = (
        '^/i18n_js$',
        '^/static/',
        # ...
    )

:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
は以下のように作動します:

* リクエストURLが :ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>` にマッチした場合、
  何もしないで、処理が終わる。
* リクエスト URL が :ref:`SSL_URLS <setting-ssl-urls>` にマッチし、リクエストが HTTP
  で来ている場合、HTTPS URLにリダイレクトする。
* リクエスト URL が :ref:`SSL_URLS <setting-ssl-urls>` にマッチしないで、
  リクエストが HTTPS で来ている場合、HTTP URLにリダイレクトする。

.. note:: 

    HTTPS で HTTP ページにアクセスすると、セキュリティが普段より高くて、
    問題が無いのですが、セキュアでないページに HTTPS でアクセスすると、 
    HTTP 用のページにリダイレクトするのは、複数のページに同じコンテンツが
    出来てしまい、検索エンジンの混乱、 `REST`_ のルールを破ることを
    避けるための操作です。

ビューでアクセスを制限する
-----------------------------------

ビューでセキュアアクセス制限をかける場合もあります。複数のURLで同じビューで
アクセスする場合もあり、ある機能へのアクセスを制限したい場合があります。
その場合、URLでアクセス制限をかけるのに合わないでしょう。

生真面目なやり方
+++++++++++++++++++++++++++++++++++

複数のURLで同じビューへアクセスする場合があるので、ビューでセキュアアクセス制限
に対応すると以下のようになります。生真面目なやり方は、ビューの中に
`request.is_secure()`_ でリクエストがセキュアかどうかをチェックします::

    from django.http import HttpResponseRedirect
    from django.http import get_host

    def my_secure_view(request):
        if request.is_secure():
            return HttpResponseRedirect("https://%s%s" % (get_host(request), request.get_full_path()))
        # ...

しかし、このやり方でやりますと、
:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
はこのビューがセキュアかどうかがわかる用がなく、URLを 
:ref:`SSL_IGNORE_URLS <setting-ssl-ignore-urls>` に追加しないと、
当ビューの処理と眩みます。

ssl_view デコレーター
+++++++++++++++++++++++++++++++++++

.. function:: beproud.django.ssl.decorators.ssl_view 

ショートカットとして、あるビューはセキュアビューであることを指定するために
:func:`ssl_view() <beproud.django.ssl.decorators.ssl_view>`
を使うことができます::

    from beproud.django.ssl.decorators import ssl_view 

    @ssl_view
    def my_secure_view(request):
        ...

:func:`ssl_view() <beproud.django.ssl.decorators.ssl_view>`
は :class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
と同じ処理を実装しますが、 :ref:`SSL_URLS <setting-ssl-urls>` にURLを設定するのが不要に
なります。このビューがセキュアということが指定されているので、
:class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`
と眩みません。

HTTP リバースプロクシを利用する
-----------------------------------

.. class:: beproud.django.ssl.middleware.SSLProxyMiddleware 

:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>`
はプロクシサーバーからセキュアリクエストが来た場合、 `request.is_secure()`_ が
``True`` を返すようにリクエストオブジェクトを更新する。
:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>` と
連動するためにリバースプロクシを設定すう方法は
:ref:`ウェブサーバー設定 <install-web-server-setup>` にご参照ください。

あるリクエストがセキュアかどうかを指定するヘッダーの名前とセキュアの場合の値を
:ref:`SSL_REQUEST_HEADER <setting-ssl-request-header>` で設定する必要があります。
デフォールトの値は以下に示します。

.. code-block:: python

    SSL_REQUEST_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

:class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>` は以下の
ように作動します:

* :ref:`SSL_REQUEST_HEADER <setting-ssl-request-header>` で設定されているヘッダーの
  値がリバースプロクシから送られて来たリクエストヘッダーと一致すると、
  `request.is_secure()`_ が正値を返すように設定します。

.. note::

    `request.is_secure()`_ を使うミドルウエアがある可能性があるため、
    :class:`SSLProxyMiddleware <beproud.django.ssl.middleware.SSLProxyMiddleware>` を
    なるべく上のほうに `MIDDLEWARE_CLASSES`_ に設定すべきです。 少なくとも、
    :class:`SSLRedirectMiddleware <beproud.django.ssl.middleware.SSLRedirectMiddleware>`.
    の上に設定する必要があります。

.. _`request.path_info`: http://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.path_info
.. _`request.is_secure()`: http://docs.djangoproject.com/en/dev/ref/request-response/#django.http.HttpRequest.is_secure
.. _`REST`: http://ja.wikipedia.org/wiki/REST
.. _`MIDDLEWARE_CLASSES`: http://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
