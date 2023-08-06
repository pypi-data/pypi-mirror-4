=================
Advanced Features
=================

*Milla* contains several powerful tools that allow web developers complete
control over how their applications behave.

.. contents:: Contents
   :local:

Propagating Configuration
=========================

While one possible way for :term:`controller` callables to obtain configuration
information would be for them to read it each time a request is made, it would
be extremely inefficient. To help with this, *Milla* provides a simple
configuration dictionary that can be populated when the
:py:class:`~milla.app.Application` is created and will be available to
controllers as the :py:attr:`~milla.Request.config` attribute of the request.

.. code-block:: python

   def controller(request):
       if request.config['t_virus'] == 'escaped':
           return 'Zombies!'
       else:
           return 'Raccoon City is safe, for now'

   router = milla.dispatch.routing.Router()
   router.add_route('/', controller)
   application = milla.Application(router)
   application.config['t_virus'] = 'contained'

*Milla* provides a simple utility called :py:func:`~milla.util.read_config`
that can produce a flat dictionary from a standard configuration file:

.. code-block:: ini

   ; umbrella.ini
   [t_virus]
   status = escaped

.. code-block:: python
 
   # app.py
   class Root(object):
   
       def __call__(self, request):
           if request.config['t_virus.status'] == 'escaped':
               return 'Zombies!'
           else:
               return 'Raccoon City is safe, for now'
    
   application = milla.Application(Root())
   application.config.update(read_config('umbrella.ini'))

Notice that the section name appears in the dictionary key as well as the
option name, separated by a dot (``.``). This allows you to specify have
multiple options with the same name, as long as they are in different sections.

Allowing Various HTTP Methods
=============================

By default, *Milla* will reject HTTP requests using methods other than ``GET``,
``HEAD``, or ``OPTIONS`` by returning an `HTTP 405`_ response. If you need a
controller callable to accept these requests, you need to explicitly specify
which methods are allowed.

To change the request methods that a controller callable accepts, use the
:py:meth:`~milla.allow` decorator.

.. code-block:: python

   @milla.allow('GET', 'HEAD', 'POST')
   def controller(request):
       response = request.ResponseClass()
       if request.method == 'POST':
           release_t_virus()
           response.text = 'The T Virus has been released. Beware of Zombies'
           return response
       else:
           status = check_t_virus()
           response.text = 'The T Virus is {0}'.format(status)
           return response

.. note:: You do not need to explicitly allow the ``OPTIONS`` method; it is
   always allowed. If an ``OPTIONS`` request is made, *Milla* will
   automatically create a valid response informing the user of the allowed HTTP
   request methods for the given request path. Your controller will not be
   called in this case.

Controlling Access
==================

*Milla* provides a powerful and extensible authorization framework that can be
used to restrict access to different parts of a web application based on
properties of the request. This framework has two major components---request
validators and permission requirements. To use the framework, you must
implement a :term:`request validator` and then apply a :term:`permission
requirement` decorator to your :py:term:`controller` callables as needed.

Request Validators
******************

The default request validator (:py:class:`milla.auth.RequestValidator`) is
likely sufficient for most needs, as it assumes that a user is associated with
a request (via the ``user`` attribute on the :py:class:`~milla.Request` object)
and that the user has a ``permissions`` attribute that contains a list of
permissions the user holds.

.. note:: *Milla* does not automatically add a ``user`` attribute to
   ``Request`` instances, nor does it provide any way of determining what
   permissions the user has. As such, you will need to handle both of these on
   your own by utilizing the :ref:`before-after-hooks`.

Request validators are classes that have a ``validate`` method that takes a
request and optionally a permission requirement. The ``validate`` method should
return ``None`` if the request meets the requirements or raise
:py:exc:`~milla.auth.NotAuthorized` (or a subclass thereof) if it does not.
This exception will be called as the controller instead of the actual
controller if the request is not valid.

If you'd like to customize the response to invalid requests or the default
request validator is otherwise insufficient for your needs, you can create your
own request validator. To do this, you need to do the following:

1. Create a subclass of :py:class:`~milla.auth.RequestValidator` that overrides
   :py:meth:`~milla.auth.RequestValidator.validate` method (taking care to
   return ``None`` for valid requests and raise a subclass of
   :py:exc:`~milla.auth.NotAuthorized` for invalid requests)
2. Register the new request validator in the ``milla.request_validator`` entry
   point group in your ``setup.py``

   For example:

   .. code-block:: python

      setup(name='UmbrellaCorpWeb',
            ...
            entry_points={
                'milla.request_validator': [
                    'html_login = umbrellacorpweb.lib:RequestValidatorLogin'
                ],
            },
      )
3. Set the ``request_validator`` application config key to the entry point name
   of the new request validator

   For example:

   .. code-block:: python
      
      application = milla.Application(Root())
      application.config['request_validator'] = 'html_login'

Permission Requirements
***********************

Permission requirements are used by request validators to check whether or not
a request is authorized for a particular controller. Permission requirements
are applied to controller callables by using the
:py:meth:`~milla.auth.decorators.require_perms` decorator.

.. code-block:: python

   class Root(object):

       def __call__(self, request):
           return 'This controller requires no permission'

       @milla.require_perms('priority1')
       def special(self, request):
           return 'This controller requires Priority 1 permission'

You can specify advanced permission requirements by using
:py:class:`~milla.auth.permissions.Permission` objects:

.. code-block:: python

   class Root(object):

       def __call__(self, request):
           return 'This controller requires no permission'

       @milla.require_perms(Permission('priority1') | Permission('alpha2'))
       def special(self, request):
           return 'This controller requires Priority 1 or Alpha 2 permission'

Example
*******

The following example will demonstrate how to define a custom request validator
that presents an HTML form to the user for failed requests, allowing them to
log in:

``setup.py``:

.. code-block:: python

   from setuptools import setup

   setup(name='MyMillaApp',
         version='1.0',
         install_requires='Milla',
         py_modules=['mymillaapp'],
         entry_points={
             'milla.request_validator': [
                 'html_login = mymillaapp:RequestValidatorLogin',
             ],
         },
   )

``mymillaapp.py``:

.. code-block:: python

   import milla
   import milla.auth

   class NotAuthorizedLogin(milla.auth.NotAuthorized):

       def __call__(self, request):
           response = request.ResponseClass()
           response.text = '''\
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <title>Please Log In</title>
     <meta charset="UTF-8">
   </head>
   <body>
   <h1>Please Log In</h1>
   <div style="color: #ff0000;">{error}</div>
   <form action="login" method="post">
   <div>Username:</div>
   <div><input type="text" name="username"></div>
   <div>Password:</div>
   <div><input type="password" name="password"></div>
   <div><button type="submit">Submit</button></div>
   </form>
   </body>
   </html>'''.format(error=self)
           response.status_int = 401
           response.headers['WWW-Authenticate'] = 'HTML-Form'
           return response

   class RequestValidatorLogin(milla.auth.RequestValidator):

       exc_class = NotAuthorizedLogin

   class Root(object):

       def __before__(self, request):
           # Actually determining the user from the request is beyond the
           # scope of this example. You'll probably want to use a cookie-
           # based session and a database for this.
           request.user = get_user_from_request(request)

       @milla.require_perms('kill_zombies')
       def kill_zombies(self, request):
           response = request.ResponseClass()
           response.text = 'You can kill zombies'
           return response
       
       def __call__(self, request):
           response = request.ResponseClass()
           response.text = "Nothing to see here. No zombies, that's for sure"
           return response

   application = milla.Application(Root())

.. _HTTP 405: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.6
