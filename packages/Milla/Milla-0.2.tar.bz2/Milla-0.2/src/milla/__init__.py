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
'''Milla is an extremely simple WSGI framework for web applications

'''

from milla.app import *
from milla.auth.decorators import *
from webob.exc import *
import webob
try:
    import urllib.parse
except ImportError: #pragma: no cover
    import urllib
    import urlparse
    urllib.parse = urlparse
    urllib.parse.urlencode = urllib.urlencode #@UndefinedVariable

def allow(*methods):
    '''Specify the allowed HTTP verbs for a controller callable
    
    Example::
    
        @milla.allow('GET', 'POST')
        def controller(request):
            return 'Hello, world!'
    '''

    def wrapper(func):
        func.allowed_methods = methods
        return func
    return wrapper


class Response(webob.Response):
    ''':py:class:`WebOb Response <webob.response.Response>` with minor tweaks
    '''


class Request(webob.Request):
    ''':py:class:`WebOb Request <webob.request.BaseRequest>` with minor tweaks
    '''

    ResponseClass = Response

    @classmethod
    def blank(cls, path, *args, **kwargs):
        '''Create a simple request for the specified path 
        
        See :py:meth:`webob.Request.blank <webob.request.BaseRequest.blank>`
        for information on other arguments and keywords
        '''
        
        req = super(Request, cls).blank(path, *args, **kwargs)
        req.config = {}
        return req

    def create_href(self, path, **keywords):
        '''Combine the application's path with a path to form an HREF

        :param path: relative path to join with the request URL

        Any other keyword arguments will be encoded and appended to the URL
        as querystring arguments.
        
        The HREF returned will will be the absolute path on the same host
        and protocol as the request. To get the full URL including scheme
        and host information, use :py:meth:`create_href_full` instead.
        '''

        url = self._merge_url(self.script_name, path)

        if keywords:
            url += '?' + urllib.parse.urlencode(keywords)

        return url

    def create_href_full(self, path, **keywords):
        '''Combine the application's full URL with a path to form a new URL
        
        :param path: relative path to join with the request URL
        
        Any other keyword arguments will be encoded and appended to the
        URL as querystring arguments/
        
        The HREF returned will be the full URL, including scheme and host
        information. To get the path only, use :py:meth:`create_href`
        instead.
        '''
        
        url = self._merge_url(self.application_url, path)
        
        if keywords:
            url += '?' + urllib.parse.urlencode(keywords)
        
        return url

    def static_resource(self, path):
        '''Return a URL to the given static resource

        This method combines the defined static resource root URL with the
        given path to construct a complete URL to the given resource. The
        resource root should be defined in the application configuration
        dictionary, under the name ``milla.static_root``, for example::

            app = milla.Application(dispatcher)
            app.config.update({
                'milla.static_root': '/static/'
            })

        Then, calling ``static_resource`` on a :py:class:`Request` object
        (i.e. inside a controller callable) would combine the given path
        with ``/static/``, like this::

            request.static_resource('/images/foo.png')

        would return ``/static/images/foo.png``.

        If no ``milla.static_root`` key is found in the configuration
        dictionary, the path will be returned unaltered.

        :param path: Path to the resource, relative to the defined root
        '''

        try:
            root = self.config['milla.static_root']
        except KeyError:
            return path

        return self._merge_url(root, path)

    def _merge_url(self, root, path):
        if path.startswith('/'):
            path = path[1:]
        if not root.endswith('/'):
            root += '/'

        return urllib.parse.urljoin(root, path)
