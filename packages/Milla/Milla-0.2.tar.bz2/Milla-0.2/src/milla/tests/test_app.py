'''Tests for the main Application logic

:Created: Nov 27, 2012
:Author: dustin
'''
import functools
import milla.app
import milla.dispatch
import nose.tools
import wsgiref.util
import webob.exc

class StubResolver(object):
    '''Stub resolver for testing purposes'''

    def __init__(self, controller=None):
        if not controller:
            def controller(request):
                return 'success'
        self.controller = controller

    def resolve(self, path_info):
        return self.controller

class StubResolverUnresolved(object):
    '''Stub resolver that always raises UnresolvedPath'''

    def resolve(self, path_info):
        raise milla.dispatch.UnresolvedPath()

class ResponseMaker(object):

    def __init__(self, http_version=1.1):
        self.http_version = http_version
        self.headers = ''
        self.body = b''

    def start_response(self, status, response_headers):
        self.headers += 'HTTP/{0} {1}\r\n'.format(self.http_version, status)
        for header, value in response_headers:
            self.headers += '{0}: {1}\r\n'.format(header, value)

    def finish_response(self, app_iter):
        for data in app_iter:
            self.body += data

def environ_for_testing():
    environ = {}
    wsgiref.util.setup_testing_defaults(environ)
    return environ

class AfterCalled(Exception):
    '''Raised in tests for the __after__ method'''

class BeforeCalled(Exception):
    '''Raised in tests for the __before__ method'''


def test_notfound():
    '''Application returns a 404 response for unresolved paths
    '''

    app = milla.app.Application(StubResolverUnresolved())
    environ = environ_for_testing()
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.headers.startswith('HTTP/1.1 404'), response.headers

def test_favicon():
    '''Application returns the default favicon image when requested
    '''

    app = milla.app.Application(StubResolverUnresolved())
    environ = environ_for_testing()
    environ.update({'PATH_INFO': '/favicon.ico'})
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.headers.startswith('HTTP/1.1 200'), response.headers
    assert response.body.startswith(b'\x00\x00\x01\x00'), response.body

def test_allow_header_disallowed():
    '''HTTP 405 is returned for disallowed HTTP request methods
    '''

    app = milla.app.Application(StubResolver())
    environ = environ_for_testing()
    environ.update({'REQUEST_METHOD': 'POST'})
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.headers.startswith('HTTP/1.1 405'), response.headers

def test_allow_header_allowed():
    '''HTTP 405 is not returned for explicitly allowed HTTP request methods
    '''

    resolver = StubResolver()
    resolver.controller.allowed_methods = ('POST',)
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    environ.update({'REQUEST_METHOD': 'POST'})
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.headers.startswith('HTTP/1.1 200'), response.headers

def test_allow_header_options():
    '''HTTP OPTIONS requests returns HTTP 200
    '''

    resolver = StubResolver()
    resolver.controller.allowed_methods = ('GET',)
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    environ.update({'REQUEST_METHOD': 'OPTIONS'})
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.headers.startswith('HTTP/1.1 200'), response.headers

def test_emulated_method():
    '''Emulated HTTP methods are interpreted correctly
    
    For applications that cannot use the proper HTTP method and instead
    use HTTP POST with an ``_method`` parameter
    '''

    resolver = StubResolver()
    resolver.controller.allowed_methods = ('PUT',)
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    environ.update({
        'REQUEST_METHOD': 'POST',
        'CONTENT_TYPE': 'application/x-www-form-urlencoded',
        'CONTENT_LENGTH': '11'
    })
    body = environ['wsgi.input']
    body.seek(0)
    body.write(b'_method=PUT')
    body.seek(0)
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.headers.startswith('HTTP/1.1 200'), response.headers

@nose.tools.raises(BeforeCalled)
def test_function_before():
    '''__before__ attribute is called for controller functions
    '''

    def before(request):
        raise BeforeCalled()

    resolver = StubResolver()
    resolver.controller.__before__ = before
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(BeforeCalled)
def test_instance_before():
    '''Class's __before__ is called for controller instances
    '''

    class Controller(object):
        def __before__(self, request):
            raise BeforeCalled()
        def __call__(self, request):
            return 'success'

    app = milla.app.Application(StubResolver(Controller()))
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(BeforeCalled)
def test_instancemethod_before():
    '''Class's __before__ is called for controller instance methods
    '''

    class Controller(object):
        def __before__(self, request):
            raise BeforeCalled()
        def foo(self, request):
            return 'success'

    app = milla.app.Application(StubResolver(Controller().foo))
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(BeforeCalled)
def test_partial_function_before():
    '''__before__ attribute is called for wrapped controller functions
    '''

    def before(request):
        raise BeforeCalled()
    def controller(request, text):
        return text
    controller.__before__ = before

    resolver = StubResolver()
    resolver.controller = functools.partial(controller, text='success')
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(BeforeCalled)
def test_partial_instance_before():
    '''Class's __before__ is called for wrapped controller instances
    '''

    class Controller(object):
        def __before__(self, request):
            raise BeforeCalled()
        def __call__(self, request, text):
            return text

    resolver = StubResolver()
    resolver.controller = functools.partial(Controller(), text='success')
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(BeforeCalled)
def test_partial_instancemethod_before():
    '''Class's __before__ is called for wrapped controller instance methods
    '''

    class Controller(object):
        def __before__(self, request):
            raise BeforeCalled()
        def foo(self, request, text):
            if not hasattr(request, 'before_called'):
                return 'before not called'
            else:
                return text

    resolver = StubResolver()
    resolver.controller = functools.partial(Controller().foo, text='success')
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(AfterCalled)
def test_function_after():
    '''__after__ attribute is called for controller functions
    '''

    def after(request):
        raise AfterCalled()

    resolver = StubResolver()
    resolver.controller.__after__ = after
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(AfterCalled)
def test_instance_after():
    '''Class's __after__ is called for controller instances
    '''

    class Controller(object):
        def __after__(self, request):
            raise AfterCalled()
        def __call__(self, request):
            return 'success'

    app = milla.app.Application(StubResolver(Controller()))
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(AfterCalled)
def test_instancemethod_after():
    '''Class's __after__ is called for controller instance methods
    '''

    class Controller(object):
        def __after__(self, request):
            raise AfterCalled()
        def foo(self, request):
            return 'success'

    app = milla.app.Application(StubResolver(Controller().foo))
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(AfterCalled)
def test_partial_function_after():
    '''__after__ attribute is called for wrapped controller functions
    '''

    def after(request):
        raise AfterCalled()
    def controller(request, text):
        return text
    controller.__after__ = after

    resolver = StubResolver()
    resolver.controller = functools.partial(controller, text='success')
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(AfterCalled)
def test_partial_instance_after():
    '''Class's __after__ is called for wrapped controller instances
    '''

    class Controller(object):
        def __after__(self, request):
            raise AfterCalled()
        def __call__(self, request, text):
            return text

    resolver = StubResolver()
    resolver.controller = functools.partial(Controller(), text='success')
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

@nose.tools.raises(AfterCalled)
def test_partial_instancemethod_after():
    '''Class's __after__ is called for wrapped controller instance methods
    '''

    class Controller(object):
        def __after__(self, request):
            raise AfterCalled()
        def foo(self, request, text):
            if not hasattr(request, 'after_called'):
                return 'after not called'
            else:
                return text

    resolver = StubResolver()
    resolver.controller = functools.partial(Controller().foo, text='success')
    app = milla.app.Application(resolver)
    environ = environ_for_testing()
    response = ResponseMaker()
    app(environ, response.start_response)

def test_httperror_response():
    '''HTTPErrors raised by controllers should used as the response
    '''

    def controller(request):
        raise webob.exc.HTTPClientError('NotFound')

    app = milla.app.Application(StubResolver(controller))
    environ = environ_for_testing()
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.headers.startswith('HTTP/1.1 400'), response.headers
    assert b'NotFound' in response.body, response.body

def test_single_start_response():
    '''Ensure start_response is only called once'''

    class TestStartResponse(object):
        def __init__(self, func):
            self.call_count = 0
            self.func = func
        def __call__(self, *args, **kwargs):
            self.call_count += 1
            return self.func(*args, **kwargs)

    def controller(request):
        status = '200 OK'
        headers = [('Content-Type', 'text/plain')]
        request.start_response(status, headers)
        return 'test'

    app = milla.app.Application(StubResolver(controller))
    environ = environ_for_testing()
    response = ResponseMaker()
    start_response = TestStartResponse(response.start_response)
    app_iter = app(environ, start_response)
    response.finish_response(app_iter)
    assert start_response.call_count == 1, start_response.call_count
    assert response.headers.startswith('HTTP/1.1 200 OK'), response.headers
    assert response.body == b'test', response.body

def test_allow_decorator():
    '''Ensure allow decorator sets allowed_methods on controllers'''

    @milla.allow('GET', 'HEAD', 'POST')
    def controller(request):
        return 'success'

    assert controller.allowed_methods == ('GET', 'HEAD', 'POST')

def test_create_href_simple():
    '''Request.create_href creates a valid URL path from the application root'''

    environ = environ_for_testing()
    request = milla.Request(environ)
    url = request.create_href('/bar')
    assert url == '/bar', url

def test_create_href_nonroot():
    '''Request.create_href handles applications mounted somewhere besides /'''

    environ = environ_for_testing()
    environ.update({
        'SCRIPT_NAME': '/test'
    })
    request = milla.Request(environ)
    url = request.create_href('/bar')
    assert url == '/test/bar', url

def test_create_href_full():
    '''Request.create_href_full creates appropriate full URL'''

    environ = environ_for_testing()
    request = milla.Request(environ)
    url = request.create_href_full('/bar')
    assert url == 'http://127.0.0.1/bar', url

def test_create_href_full_nonroot():
    '''Request.create_href_full creates correct full URL for nonroot applications'''

    environ = environ_for_testing()
    environ.update({
        'SCRIPT_NAME': '/test'
    })
    request = milla.Request(environ)
    url = request.create_href_full('/bar')
    assert url == 'http://127.0.0.1/test/bar', url

def test_create_href_keywords():
    '''Request.create_href properly appends querystring arguments'''

    environ = environ_for_testing()
    request = milla.Request(environ)
    url = request.create_href('/bar', foo='baz')
    assert url == '/bar?foo=baz'

def test_create_href_full_keywords():
    '''Request.create_href_full properly appends querystring arguments'''

    environ = environ_for_testing()
    request = milla.Request(environ)
    url = request.create_href_full('/bar', foo='baz')
    assert url == 'http://127.0.0.1/bar?foo=baz'

def test_static_resource():
    '''Request.static_resource creates valid URL from config'''
    
    def controller(request):
        return request.static_resource('/image.png')
    
    environ = environ_for_testing()
    app = milla.Application(StubResolver(controller))
    app.config['milla.static_root'] = '/static'
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.body == b'/static/image.png', response.body

def test_static_resource_undefined():
    '''Request.static_resource returns the path unmodified with no root defined'''
    
    def controller(request):
        return request.static_resource('/image.png')
    
    environ = environ_for_testing()
    app = milla.Application(StubResolver(controller))
    response = ResponseMaker()
    app_iter = app(environ, response.start_response)
    response.finish_response(app_iter)
    assert response.body == b'/image.png', response.body
    