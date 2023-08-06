===============
Getting Started
===============

*Milla* aims to be lightweight and easy to use. As such, it provides only the
tools you need to build your application the way you want, without imposing any
restrictions on how to do it.

.. contents:: Contents
   :local:

Milla's Components
==================

*Milla* provides a small set of components that help you build your web
application in a simple, efficient manner:

* WSGI Application wrapper
* Two types of URL Dispatchers:
  
  * Traversal (like CherryPy or Pyramid)
  * Routing (like Django or Pylons)

* Authorization framework
* Utility functions

*Milla* does not provide an HTTP server, so you'll have to use one of the many
implementations already available, such as `Meinheld`_ or `Paste`_, or another
application that understands `WSGI`_, like `Apache HTTPD`_ with the `mod_wsgi`_
module.

``Application`` Objects
=======================

The core class in a *Milla*-based project is its
:py:class:`~milla.app.Application` object. ``Application`` objects are used to
set up the environment for the application and handle incoming requests.
``Application`` instances are *WSGI* callables, meaning they implement the
standard ``application(environ, start_response)`` signature.

To set up an ``Application``, you will need a :term:`URL dispatcher`, which is
an object that maps request paths to :term:`controller` callables.

Choosing a URL Dispatcher
=========================

*Milla* provides two types of URL dispatchers by default, but you can create
your own if neither of these suit your needs. The default dispatchers are
modeled after the URL dispatchers of other popular web frameworks, but may have
small differences.

A *Milla* application can only have one URL dispatcher, so make sure you choose
the one that will work for all of your application's needs.

Traversal
*********

Object traversal is the simplest form of URL dispatcher, and is the default for
*Milla* applications. Object traversal works by looking for path segments as
object attributes, beginning with a :term:`root object` until a
:term:`controller` is found.

For example, consider the URL ``http://example.org/myapp/hello``. Assuming the
*Milla* application is available at ``/myapp`` (which is controlled by the HTTP
server), then the ``/hello`` portion becomes the request path. It contains only
one segment, ``hello``. Thus, an attribute called ``hello`` on the :term:`root
object` must be the controller that will produce a response to that request.
The following code snippet will produce just such an object.

.. code-block:: python

   class Root(object):

       def hello(self, request):
          return 'Hello, world!'

To use this class as the :term:`root object` for a *Milla* application, pass an
instance of it to the :py:class:`~milla.app.Application` constructor:

.. code-block:: python

   application = milla.Application(Root())

To create URL paths with multiple segments, such as ``/hello/world`` or
``/umbrella/corp/bio``, the root object will need to have other objects
corresponding to path segments as its attributes.

This example uses static methods and nested classes:

.. code-block:: python

   class Root(object):
   
       class hello(object):
           
           @staticmethod
           def world(request):
               return 'Hello, world!'
   
   application = milla.Application(Root)

This example uses instance methods to create the hierarchy at runtime:

.. code-block:: python

   class Root(object):

       def __init__(self):
           self.umbrella = Umbrella()

   class Umbrella(object):

       def __init__(self):
           self.corp = Corp()
   
   class Corp(object):

       def bio(self, request):
           return 'T-Virus research facility'

   application = milla.Application(Root())

If an attribute with the name of the next path segment cannot be found, *Milla*
will look for a ``default`` attribute.

While the object traversal dispatch mechanism is simple, it is not very
flexible. Because path segments correspond to Python object names, they must
adhere to the same restrictions. This means they can only contain ASCII letters
and numbers and the underscore (``_``) character. If you need more complex
names, dynamic segments, or otherwise more control over the path mapping, you
may need to use routing.

Routing
*******

Routing offers more control of how URL paths are mapped to :term:`controller`
callables, but require more specific configuration.

To use routing, you need to instantiate a
:py:class:`~milla.dispatch.routing.Router` object and then populate its routing
table with path-to-controller maps. This is done using the
:py:meth:`~milla.dispatch.routing.Router.add_route` method.

.. code-block:: python

   def hello(request):
       return 'Hello, world!'

   router = milla.dispatch.routing.Router()
   router.add_route('/hello', hello)

Aft er you've set up a ``Router`` and populated its routing table, pass it to
the :py:class:`~milla.app.Application` constructor to use it in a *Milla*
application:

.. code-block:: python

   application = milla.Application(router)

Using routing allows paths to contain dynamic portions which will be passed to
controller callables as keyword arguments.

.. code-block:: python

   def hello(request, name):
       return 'Hello, {0}'.format(name)

   router = milla.dispatch.routing.Router()
   router.add_route('/hello/{name}', hello)
   
   application = milla.Application(router)

In the above example, the path ``/hello/alice`` would map to the ``hello``
function, and would return the response ``Hello, alice`` when visited.

``Router`` instances can have any number of routes in their routing table. To
add more routes, simply call ``add_route`` for each path and controller
combination you want to expose.

.. code-block:: python

   def hello(request):
       return 'Hello, world!'
    
   def tvirus(request):
       return 'Beware of zombies'
    
   router = milla.dispatch.routing.Router()
   router.add_route('/hello', hello)
   router.add_route('/hello-world', hello)
   router.add_route('/umbrellacorp/tvirus', tvirus)

Controller Callables
====================

*Controller callables* are where most of your application's logic will take
place. Based on the :abbr:`MVC (Model, View, Controller)` pattern, controllers
handle the logic of interaction between the user interface (the *view*) and the
data (the *model*). In the context of a *Milla*-based web application,
controllers take input (the HTTP request, represented by a
:py:class:`~milla.Request` object) and deliver output (the HTTP response,
represented by a :py:class:`~milla.Response` object).

Once you've decided which URL dispatcher you will use, it's time to write
controller callables. These can be any type of Python callable, including
functions, instance methods, classmethods, or partials. *Milla* will
automatically determine the callable type and call it appropriately for each
controller callable mapped to a request path.

This example shows a controller callable as a function (using routing):

.. code-block:: python

   def index(request):
       return 'this is the index page'

   def hello(request):
       return 'hello, world'

   router = milla.dispatch.routing.Router()
   router.add_route('/', index)
   router.add_route('/hello', hello)
   application = milla.Application(router)

This example is equivalent to the first, but shows a controller callable as a
class instance (using traversal):

.. code-block:: python

   class Controller(object):

       def __call__(self, request):
           return 'this is the index page'

       def hello(self, request):
           return 'hello, world'

   application = milla.Application(Controller())

Controller callables must take at least one argument, which will be an instance
of :py:class:`~milla.Request` representing the HTTP request that was made by
the user. The ``Request`` instance wraps the *WSGI* environment and exposes all
of the available information from the HTTP headers, including path, method
name, query string variables, POST data, etc.

If you are using `Routing`_ and have routes with dynamic path segments, these
segments will be passed by name as keyword arguments, so make sure your
controller callables accept the same keywords.

.. _before-after-hooks:

Before and After Hooks
**********************

You can instruct *Milla* to perform additional operations before and after the
controller callable is run. This could, for example, create a `SQLAlchemy`_
session before the controller is called and roll back any outstanding
transactions after it completes.

To define the before and after hooks, create an ``__before__`` and/or an
``__after__`` attribute on your controller callable. These attributes should be
methods that take exactly one argument: the request. For example:

.. code-block:: python

   def setup(request):
        request.user = 'Alice'
    
   def teardown(request):
        del request.user
    
   def controller(request):
       return 'Hello, {user}!'.format(user=request.user)
   controller.__before__ = setup
   controller.__after__ = teardown

To simplify this, *Milla* handles instance methods specially, by looking for
the ``__before__`` and ``__after__`` methods on the controller callable's class
as well as itself.

.. code-block:: python

   class Controller(object):
    
       def __before__(self, request):
           request.user = 'Alice'
       
       def __after__(self, request):
           del request.user
     
       def __call__(self, request):
           return 'Hello, {user}'.format(user=request.user)

Returing a Response
===================

Up until now, the examples have shown :term:`controller` callables returning a
string. This is the simplest way to return a plain HTML response; *Milla* will
automatically send the appropriate HTTP headers for you in this case. If,
however, you need to send special headers, change the content type, or stream
data instead of sending a single response, you will need to return a
:py:class:`~milla.Response` object. This object contains all the properties
necessary to instruct *Milla* on what headers to send, etc. for your response.

To create a :py:class:`~milla.Response` instance, use the
:py:attr:`~milla.Request.ResponseClass` attribute from the request:

.. code-block:: python

   def controller(request):
       response = request.ResponseClass()
       response.content_type = 'text/plain'
       response.text = 'Hello, world!'
       return response

.. _Meinheld: http://meinheld.org/
.. _Paste: http://pythonpaste.org/
.. _WSGI: http://www.python.org/dev/peps/pep-0333/
.. _Apache HTTPD: http://httpd.apache.org/ 
.. _mod_wsgi: http://code.google.com/p/modwsgi/
.. _SQLAlchemy: http://www.sqlalchemy.org/
