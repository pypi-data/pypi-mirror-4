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
import milla.dispatch
import webob

__all__ = ['Application']

class Application(object):
    '''Represents a Milla web application
    
    Constructing an ``Application`` instance needs a dispatcher, or
    alternatively, a root object that will be passed to a new
    :py:class:`milla.dispatch.traversal.Traverser`. 
    
    :param root: A root object, passed to a traverser, which is
       automatically created if a root is given
    :param dispatcher: An object implementing the dispatcher protocol 
    
    ``Application`` instances are WSGI applications.
    
    .. py:attribute:: config
    
       A mapping of configuration settings. For each request, the
       configuration is copied and assigned to ``request.config``.
    '''

    DEFAULT_ALLOWED_METHODS = ['GET', 'HEAD', 'OPTIONS']

    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
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

        request = webob.Request(environ)
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
            return HTTPMethodNotAllowed(headers=allow_header)(environ,
                                                              start_response)

        start_response_wrapper = StartResponseWrapper(start_response)
        request.start_response = start_response_wrapper        
        try:
            # If the callable has an __before__ attribute, call it
            if hasattr(func, '__before__'):
                func.__before__(request)
            # If the callable is an instance method and its class has
            # a __before__ method, call that
            elif hasattr(func, 'im_self') and \
                hasattr(func.im_self, '__before__'):
                func.im_self.__before__(request)
            # The callable might be a partial, so check the inner func
            elif hasattr(func, 'func'):
                if hasattr(func.func, '__before__'):
                    func.func.__before__(request)
                elif hasattr(func.func, 'im_self') and \
                    hasattr(func.func.im_self, '__before__'):
                    func.func.im_self.__before__(request)
            response = func(request)
        except WSGIHTTPException as e:
            return e(environ, start_response)
        finally:
            # If the callable has an __after__ method, call it
            if hasattr(func, '__after__'):
                func.__after__(request)
            # If the callable is an instance method and its class has
            # an __after__ method, call that
            elif hasattr(func, 'im_self') and \
                hasattr(func.im_self, '__after__'):
                func.im_self.__after__(request)
            # The callable might be a partial, so check the inner func
            elif hasattr(func, 'func'):
                if hasattr(func.func, '__after__'):
                    func.func.__after__(request)
                elif hasattr(func.func, 'im_self') and \
                    hasattr(func.func.im_self, '__after__'):
                    func.func.im_self.__after__(request)

        # The callable might have returned just a string, which is OK,
        # but we need to wrap it in a WebOb response
        if isinstance(response, basestring) or not response:
            response = webob.Response(response)

        if not start_response_wrapper.called:
            start_response(response.status, response.headerlist)
        if not environ['REQUEST_METHOD'] == 'HEAD':
            return response.app_iter

class StartResponseWrapper():
    
    def __init__(self, start_response):
        self.start_response = start_response
        self.called = False
    
    def __call__(self, *args, **kwargs):
        self.called = True
        return self.start_response(*args, **kwargs)