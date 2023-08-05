bpssl ドキュメント
===================================

bpssl とは？
-----------------------------------

bpsslはDjango用のSSL対応アプリです。アクセスする時に
HTTPSが必須なURLを指定することがよくあります。例えば、ログイン画面を
HTTPSでしかアクセスできないようにする。ただし、HTTPでアクセスした場合、
HTTPSのほうのURLにリダイレクトしたいこともよくあります。 bpssl
はその対応を簡単にできるようなアプリです。

URLでも、ビューでもSSLリダイレクトに対応していますし、 `flatpages`_
にも対応しています。 `Fastcgi`_ にも、HTTP リバースプロクシーサーバーにも
対応しています。ソースを以下のURLでご覧ください。

http://bitbucket.org/beproud/bpssl/

bpssl は http://www.djangosnippets.org に投稿したSSLミドルウエアから、インスピレーションを得た。
以下のスニペットの機能にほぼ対応しています。

* http://djangosnippets.org/snippets/880/
* http://djangosnippets.org/snippets/240/
* http://djangosnippets.org/snippets/1999/

目次:

.. toctree::
  :numbered:
  :maxdepth: 2

  install
  usage 
  settings

Indices and tables
===================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _flatpages: http://djangoproject.jp/doc/ja/1.0/ref/contrib/flatpages.html
.. _fastcgi: http://djangoproject.jp/doc/ja/1.0/howto/deployment/fastcgi.html
