wsgi-proxy
==========

This package implements a simple WSGI app that does HTTP 1.0 proxy.
You can install it using ``pip`` or ``easy_install``:

.. code-block:: console

   $ pip install wsgi-proxy

You can run a proxy server using ``wsgi-proxy`` command it provides:

.. code-block:: console

   $ wsgi-proxy -p8080

It provides a WSGI application object (``wsgi_proxy:app``) as well:

.. code-block:: console

   $ pip install gunicorn
   $ gunicorn -p8080 wsgi_proxy:app


Links
-----

Docs
   https://wsgi-proxy.readthedocs.org/

Bitbucket (Mercurial repository)
   https://bitbucket.org/dahlia/wsgi-proxy

Package Index (Cheeseshop)
   https://pypi.python.org/pypi/wsgi-proxy
