'''Unit tests for the URL dispatcher

:Created: Mar 26, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''
import milla.dispatch.traversal

def test_root():
    '''Ensure the root path resolves to the root handler
    
    Given the path ``/``, the resolver should return the root handler,
    which was given to it at initialization
    '''

    class Root(object):
        pass

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    func = dispatcher.resolve('/')
    assert func == root

def test_unrelated():
    '''Ensure unrelated attributes do not confuse the dispatcher
    
    Given the path ``/`` and a root handler with attributes and 
    methods, the resolver should still return the root handler
    '''

    class Root(object):
        def test(self):
            pass
        foo = 'bar'

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    func = dispatcher.resolve('/')
    assert func == root

def test_unresolved():
    '''Ensure that the resolver returns remaining parts
    
    Given the path ``/foo/bar/baz`` and a root handler with no
    children, the resolver should raise
    :py:exc:`~milla.dispatch.UnresolvedPath`
    '''

    class Root(object):
        pass

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    try:
        dispatcher.resolve('/foo/bar/baz')
    except milla.dispatch.UnresolvedPath:
        pass
    else:
        raise AssertionError

def test_method():
    '''Ensure the resolver finds an instance method handler
    
    Given the path ``/test`` and a root handler with an instance
    method named ``test``, the resolver should return that method.
    '''

    class Root(object):
        def test(self):
            pass

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    func = dispatcher.resolve('/test')
    assert func == root.test

def test_nested_class():
    '''Ensure the resolver finds a nested class handler
    
    Given the path ``/test`` and a root handler with an inner class
    named ``test``, the resolver should return the inner class.
    '''

    class Root(object):
        class test(object):
            pass

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    func = dispatcher.resolve('/test')
    assert func == root.test

def test_nested_class_method():
    '''Ensure the resolver finds an instance method of a nested class
    
    Given the path ``/test/test`` and a root handler with an inner
    class named ``test``, which in turn has an instance method named
    ``test``, the resolver should return the ``test`` method of the
    inner class.
    '''

    class Root(object):
        class test(object):
            def test(self):
                pass

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    func = dispatcher.resolve('/test/test')
    assert func == root.test.test

def test_attribute():
    '''Ensure the resolver finds a handler in an instance attribute
    
    Given the path ``/test`` and a root handler with an attribute named
    ``test`` containing another class, the resolver should return that
    class.
    '''

    class Test(object):
        pass
    class Root(object):
        test = Test()

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    func = dispatcher.resolve('/test')
    assert func == Root.test

def test_default():
    '''Ensure the resolver finds the default handler
    
    Given the path ``/test`` and a root handler with a method named
    ``default``, but no method named ``test``, the resolver should
    return the ``default`` method. 
    '''

    class Root(object):
        def default(self):
            pass

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    func = dispatcher.resolve('/test')
    assert func == root.default

def test_nested_default():
    '''Ensure the resolver finds a nested default handler
    
    Given the path ``/test/bar`` and a root handler with a ``test``
    attribute containing a class instance with a ``default`` method but
    no ``bar`` method, the resolver should return the ``default``
    of the nested instance.
    '''

    class Test(object):
        def default(self):
            pass
    class Root(object):
        test = Test()

    root = Root()
    dispatcher = milla.dispatch.traversal.Traverser(root)
    func = dispatcher.resolve('/test/bar')
    assert func == root.test.default
