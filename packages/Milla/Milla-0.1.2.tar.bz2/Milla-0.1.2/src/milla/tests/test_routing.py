'''Tests for the routing URL dispatcher

:Created: Mar 26, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''
import milla.dispatch.routing

def fake_controller():
    pass

def test_static():
    '''Ensure the dispatcher can resolve a static path
    
    Given the path ``/foo/bar/baz`` and a route for the exact same
    path, the resolver should return the controller mapped to the
    route.
    '''

    def controller():
        pass

    router = milla.dispatch.routing.Router()
    router.add_route('/foo/bar/baz', controller)
    func = router.resolve('/foo/bar/baz')
    assert func.func == controller

def test_urlvars():
    '''Ensure the dispatcher can resolve a path with variable segments
    
    Given the path ``/foo/abc/def`` and a route ``/foo/{bar}/{baz}``,
    the resolver should return the controller mapped to the route with
    preset keywords ``bar='abc', baz='def'``.
    '''

    def controller():
        pass

    router = milla.dispatch.routing.Router()
    router.add_route('/foo/{bar}/{baz}', controller)
    func = router.resolve('/foo/abc/def')
    assert func.func == controller
    assert func.keywords['bar'] == 'abc'
    assert func.keywords['baz'] == 'def'

def test_regexp_urlvar():
    '''Ensure the dispatcher can resolve alternate regexps in urlvars
    
    Given a route ``/test/{arg:[a-z]+}``, the resolver should return
    the mapped controller for the path ``/test/abcde``, but not the
    path ``/test/1234``.
    '''

    def controller():
        pass

    router = milla.dispatch.routing.Router()
    router.add_route('/test/{arg:[a-z]+}', controller)
    func = router.resolve('/test/abcde')
    assert func.func == controller
    assert func.keywords['arg'] == 'abcde'

    try:
        func = router.resolve('/test/1234')
    except milla.dispatch.UnresolvedPath:
        pass
    else:
        raise AssertionError

def test_unresolved():
    '''Ensure the resolver raises an exception for unresolved paths
    
    Given a route ``/test``, the resolver should raise
    :py:exc:`~milla.dispatch.UnresolvedPath` for the path ``/tset``.
    '''

    def controller():
        pass

    router = milla.dispatch.routing.Router()
    router.add_route('/test', controller)
    try:
        router.resolve('/tset')
    except milla.dispatch.UnresolvedPath:
        pass
    else:
        raise AssertionError

def test_unrelated():
    '''Ensure the dispatcher is not confused by unrelated paths
    
    Given routes for ``/testA`` and ``/testB``, the resolver should
    return the controller mapped to the former for the path ``/testA``,
    without regard for the latter.
    '''

    def controller_a():
        pass

    def controller_b():
        pass

    router = milla.dispatch.routing.Router()
    router.add_route('/testA', controller_a)
    router.add_route('/testB', controller_b)
    func = router.resolve('/testA')
    assert func.func == controller_a

def test_string_controller():
    '''Ensure the dispatcher can find a controller given a string
    
    Given a string path to a controller function, the callable defined
    therein should be returned by the resolver for the corresponding
    path.
    '''

    router = milla.dispatch.routing.Router()
    router.add_route('/test', 'milla.tests.test_routing:fake_controller')
    func = router.resolve('/test')
    assert func.func == fake_controller
