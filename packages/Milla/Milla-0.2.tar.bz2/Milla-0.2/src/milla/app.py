# Copyright 2011 Dustin C. Hatch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
'''Module milla.app

Please give me a docstring!

:Created: Mar 26, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''

from milla.controllers import FaviconController
from milla.util import asbool
from webob.exc import HTTPNotFound, WSGIHTTPException, HTTPMethodNotAllowed
import milla.dispatch.traversal

__all__ = ['Application']

class Application(object):
    '''Represents a Milla web application

    Constructing an ``Application`` instance needs a dispatcher, or
    alternatively, a root object that will be passed to a new
    :py:class:`milla.dispatch.traversal.Traverser`.

    :param obj: An object implementing the dispatcher protocol, or an
       object to be used as the root for a Traverser

    ``Application`` instances are WSGI applications.

    .. py:attribute:: config

       A mapping of configuration settings. For each request, the
       configuration is copied and assigned to ``request.config``.
    '''

    DEFAULT_ALLOWED_METHODS = ['GET', 'HEAD']

    def __init__(self, obj):
        if not hasattr(obj, 'resolve'):
            # Object is not a dispatcher, but the root object for traversal
            obj = milla.dispatch.traversal.Traverser(obj)
        self.dispatcher = obj
        self.config = {'milla.favicon': True}

    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']
        try:
            func = self.dispatcher.resolve(path_info)
        except milla.dispatch.UnresolvedPath:
            if asbool(self.config.get('milla.favicon')) and \
                path_info == '/favicon.ico':
                func = FaviconController()
            else:
                return HTTPNotFound()(environ, start_response)

        request = milla.Request(environ)
        request.config = self.config.copy()

        # Sometimes, hacky applications will try to "emulate" some HTTP
        # method like POST or DELETE by specifying an _method parameter
        # in a POST request.
        if request.method == 'POST' and '_method' in request.POST:
            request.method = request.POST.pop('_method')

        allowed_methods = getattr(func, 'allowed_methods',
                                  self.DEFAULT_ALLOWED_METHODS)
        if request.method not in allowed_methods:
            allow_header = {'Allow': ', '.join(allowed_methods)}
            if request.method == 'OPTIONS':
                def options_response(request, *args, **kwargs):
                    response = request.ResponseClass()
                    response.headers = allow_header
                    return response
                func = options_response
            else:
                func = HTTPMethodNotAllowed(headers=allow_header) 
                return func(environ, start_response)

        start_response_wrapper = StartResponseWrapper(start_response)
        request.start_response = start_response_wrapper
        try:
            self._call_before(func)(request)
            response = func(request)
        except WSGIHTTPException as e:
            return e(environ, start_response)
        finally:
            self._call_after(func)(request)

        # The callable might have returned just a string, which is OK,
        # but we need to wrap it in a Response object
        try:
            # In Python 2, it could be a str or a unicode object
            basestring = basestring #@UndefinedVariable
        except NameError:
            # Python 3 has no unicode objects and thus no need for
            # basestring so we, just make it an alias for str 
            basestring = str
        if isinstance(response, basestring) or not response:
            response = request.ResponseClass(response)

        if not start_response_wrapper.called:
            start_response(response.status, response.headerlist)
        if not environ['REQUEST_METHOD'] == 'HEAD':
            return response.app_iter
    
    def _call_after(self, func):
        try:
            return self._find_attr(func, '__after__')
        except AttributeError:
            return lambda r: None

    def _call_before(self, func):
        try:
            return self._find_attr(func, '__before__')
        except AttributeError:
            return lambda r: None
    
    def _find_attr(self, obj, attr):
        try:
            # Object has the specified attribute itself
            return getattr(obj, attr)
        except AttributeError:
            # Object is a bound method; look for the attribute on the instance
            if hasattr(obj, '__self__'):
                return self._find_attr(obj.__self__, attr)
            # Object is a partial; look for the attribute on the inner function
            elif hasattr(obj, 'func'):
                return self._find_attr(obj.func, attr)
            raise

class StartResponseWrapper():

    def __init__(self, start_response):
        self.start_response = start_response
        self.called = False

    def __call__(self, *args, **kwargs):
        self.called = True
        return self.start_response(*args, **kwargs)
