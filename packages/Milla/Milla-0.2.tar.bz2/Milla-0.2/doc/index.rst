.. Milla documentation master file, created by
   sphinx-quickstart on Sun Mar 13 15:01:36 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Milla's documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 1
   
   getting-started
   advanced
   changelog
   reference/index
   glossary

*Milla* is a simple and lightweight web framework for Python. It built on top
of `WebOb`_ and thus implements the `WSGI`_ standard. It aims to be easy to use
while imposing no restrictions, allowing web developers to write code the way
they want, using the tools, platform, and extensions they choose.

Example
=======

.. code:: python

    from wsgiref import simple_server
    from milla.dispatch import routing
    import milla


    def hello(request):
        return 'Hello, world!'

    router = routing.Router()
    router.add_route('/', hello)
    app = milla.Application(router)

    httpd = simple_server.make_server('', 8080, app)
    httpd.serve_forever()

*Milla* is released under the terms of the `Apache License, version 2.0`_.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _WebOb: http://webob.org/
.. _WSGI: http://wsgi.readthedocs.org/
.. _Apache License, version 2.0: http://www.apache.org/licenses/LICENSE-2.0
