.. vim: set ft=rst :

=====
Milla
=====

*Milla* is a simple and lightweight web framework for Python. It built on top
of `WebOb`_ and thus implements the `WSGI`_ standard. It aims to be easy to use
while imposing no restrictions, allowing web developers to write code the way
they want, using the tools, platform, and extensions they choose.

To get started using *Milla* right away, visit `Downloads`_ to get the latest
version, then read the `Documentation`_.

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


.. _WebOb: http://webob.org/
.. _WSGI: http://wsgi.readthedocs.org/
.. _Downloads: https://bitbucket.org/AdmiralNemo/milla/downloads
.. _Documentation: http://milla.readthedocs.org/
