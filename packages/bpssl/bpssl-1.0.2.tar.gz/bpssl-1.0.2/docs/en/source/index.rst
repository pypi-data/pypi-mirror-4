bpssl Documentation
===================================

What is bpssl?
-----------------------------------

bpssl is a Django application that helps you support
HTTPS on your website. The main functionality is performing redirection
for HTTPS only URLs and views. For instance, if a request for your
login view '/login' is recieved over HTTP, the provided middleware can
redirect the user to the equivalent HTTPS page.

Specifying views and urls as secure is supported as are `flatpages`_. `Fastcgi`_
and HTTP proxy setups are also well supported. See the sourcecode/homepage at:

http://bitbucket.org/beproud/bpssl/

bpssl draws inspiration from the well known SSL Middleware snippets on
http://www.djangosnippets.org . It roughly supports the features of the following
snippets:

* http://djangosnippets.org/snippets/880/
* http://djangosnippets.org/snippets/240/
* http://djangosnippets.org/snippets/1999/

Contents:

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

.. _`flatpages`: http://docs.djangoproject.com/en/dev/ref/contrib/flatpages/
.. _Fastcgi: http://docs.djangoproject.com/en/dev/howto/deployment/fastcgi
