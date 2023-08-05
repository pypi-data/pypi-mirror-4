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
'''URL router

:Created: Mar 13, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''

from milla.dispatch import UnresolvedPath
import functools
import milla
import re
import sys
import urllib
import urlparse

class Router(object):
    '''A dispatcher that maps arbitrary paths to controller callables
    
    Typical usage::
    
        router = Router()
        router.add_route('/foo/{bar}/{baz:\d+}', some_func)
        app = milla.Application(dispatcher=router)
    
    In many cases, paths with trailing slashes need special handling.
    The ``Router`` has two ways of dealing with requests that should
    have a trailing slash but do not. The default is to send the client
    an HTTP 301 Moved Permanently response, and the other is to
    simply treat the request as if it had the necessary trailing slash.
    A third option is to disable special handling entirely and simply
    return HTTP 404 Not Found for requests with missing trailing
    slashes. To change the behavior, pass a different value to the
    constructor's ``trailing_slash`` keyword.
    
    Redirect the client to the proper path (the default)::
    
        router = Router(trailing_slash=Router.REDIRECT)
        router.add_route('/my_collection/', some_func)
    
    Pretend the request had a trailing slash, even if it didn't::
    
        router = Router(trailing_slash=Router.SILENT)
        router.add_route('/my_collection/', some_func)
    
    Do nothing, let the client get a 404 error::
    
       router = Router(trailing_slash=None)
       router.add_route('/my_collection/', some_func)
    '''

    class REDIRECT(object): pass
    class SILENT(object): pass

    #: Compiled regular expression for variable segments
    template_re = re.compile(r'\{(\w+)(?::([^}]+))?\}')

    def __init__(self, trailing_slash=REDIRECT):
        self.routes = []
        self._cache = {}
        self.trailing_slash = trailing_slash

    def resolve(self, path_info):
        '''Find a controller for a given path
        
        :param path_info: Path for which to locate a controller
        :returns: A :py:class:`functools.partial` instance that sets
          the values collected from variable segments as keyword
          arguments to the callable 
        
        This method walks through the routing table created with calls
        to :py:meth:`add_route` and finds the first whose template
        matches the given path. Variable segments are added as keywords
        to the controller function.
        '''

        def lookup(path_info):
            for regex, controller, vars in self.routes:
                match = regex.match(path_info)
                if match:
                    urlvars = match.groupdict()
                    urlvars.update(vars)
                    func = functools.partial(controller, **urlvars)
                    # Work around for Python Issue 3445 for older versions
                    for attr in functools.WRAPPER_ASSIGNMENTS:
                        try:
                            value = getattr(controller, attr)
                        except AttributeError:
                            pass
                        else:
                            setattr(func, attr, value)
                    for attr in functools.WRAPPER_UPDATES:
                        getattr(func, attr).update(getattr(controller,
                                                           attr, {}))
                    self._cache[path_info] = func
                    return func

        try:
            return self._cache[path_info]
        except KeyError:
            func = lookup(path_info)
            if func:
                return func
            elif self.trailing_slash and not path_info.endswith('/'):
                # Try to resolve the path with a trailing slash
                new_path_info = path_info + '/'
                func = lookup(new_path_info)
                if func and self.trailing_slash is Router.REDIRECT:
                    # Return a dummy function that just raises
                    # HTTPMovedPermanently to redirect the client to
                    # the canonical URL
                    def redir(*args, **kwargs):
                        raise milla.HTTPMovedPermanently(location=new_path_info)
                    return redir
                elif func and self.trailing_slash is Router.SILENT:
                    # Return the function found at the alternate path
                    return func
        raise UnresolvedPath

    def _compile_template(self, template):
        '''Compiles a template into a real regular expression
        
        :param template: A route template string
        
        Converts the ``{name}`` or ``{name:regexp}`` syntax into a full
        regular expression for later parsing.
        '''

        regex = ''
        last_pos = 0
        for match in self.template_re.finditer(template):
            regex += re.escape(template[last_pos:match.start()])
            var_name = match.group(1)
            expr = match.group(2) or '[^/]+'
            expr = '(?P<%s>%s)' % (var_name, expr)
            regex += expr
            last_pos = match.end()
        regex += re.escape(template[last_pos:])
        regex = '^%s$' % regex
        return re.compile(regex)

    def _import_controller(self, name):
        '''Resolves a string Python path to a callable'''

        module_name, func_name = name.split(':', 1)
        __import__(module_name)
        module = sys.modules[module_name]
        func = getattr(module, func_name)
        return func

    def add_route(self, template, controller, **vars):
        '''Add a route to the routing table
        
        :param template: Route template string
        :param controller: Controller callable or string Python path
        
        Route template strings are path segments, beginning with ``/``.
        Paths can also contain variable segments, delimited with curly
        braces.
        
        Example::
        
            /some/other/{variable}/{path}
        
        By default, variable segments will match any character except a
        ``/``. Alternate expressions can be passed by specifying them
        alongside the name, separated by a ``:``.
        
        Example::
        
           /some/other/{alternate:[a-zA-Z]}
        
        Variable path segments will be passed as keywords to the
        controller. In the first example above, assuming ``controller``
        is the name of the callable passed, and the request path was
        ``/some/other/great/place``::
        
            controller(request, variable='great', path='place')
        
        The ``controller`` argument itself can be any callable that
        accepts a *WebOb* request as its first argument, and any
        keywords that may be passed from variable segments. It can
        also be a string Python path to such a callable. For example::
        
            `some.module:function`
        
        This string will resolve to the function ``function`` in the
        module ``some.module``.
        '''

        if isinstance(controller, basestring):
            controller = self._import_controller(controller)
        self.routes.append((self._compile_template(template),
                            controller, vars))

class Generator(object):
    '''URL generator
    
    Creates URL references based on a *WebOb* request.
    
    Typical usage:
    
    >>> generator = Generator(request)
    >>> generator.generate('foo', 'bar')
    '/foo/bar'
    
    A common pattern is to wrap this in a stub function::
    
       url = Generator(request).generate
    '''

    def __init__(self, request, path_only=True):
        self.request = request
        self.path_only = path_only

    def generate(self, *segments, **vars):
        '''Combines segments and the application's URL into a new URL
        '''

        path = '/'.join(str(s) for s in segments)
        while path.startswith('/'):
            path = path[1:]

        url = self.request.relative_url(path, to_application=True)
        if self.path_only:
            split = urlparse.urlsplit(url)
            url = split.path
        if vars:
            url += '?' + urllib.urlencode(vars)
        return url
