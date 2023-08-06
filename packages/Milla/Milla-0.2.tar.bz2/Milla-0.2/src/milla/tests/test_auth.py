'''Tests for the Authentication/Authorization framework

:Created: Nov 27, 2012
:Author: dustin
'''
import milla.auth
import nose.tools


def test_permission_check():
    '''Ensure Permission.check returns True for lists of strings
    '''
    
    perm = milla.auth.permissions.Permission('foo')
    assert perm.check(['foo'])

def test_permission_check_false():
    '''Ensure Permission.check returns False for lists of strings
    '''
    
    perm = milla.auth.permissions.Permission('foo')
    assert not perm.check(['bar'])

def test_permission_check_perm():
    '''Ensure Permission.check returns True for lists of Permissions
    '''
    
    req = milla.auth.permissions.Permission('foo')
    perm = milla.auth.permissions.Permission('foo')
    assert req.check([perm])

def test_permission_check_perm_false():
    '''Ensure Permission.check returns True for lists of Permissions
    '''
    
    req = milla.auth.permissions.Permission('foo')
    perm = milla.auth.permissions.Permission('bar')
    assert not req.check([perm])

def test_permission_check_container():
    '''Ensure Permission.check returns True for PermissionContainers of strings
    '''
    
    perm = milla.auth.permissions.Permission('foo')
    container = milla.auth.permissions.PermissionContainer(['foo'])
    assert perm.check(container)

def test_permission_check_container_false():
    '''Ensure Permission.check returns True for PermissionContainers of strings
    '''
    
    perm = milla.auth.permissions.Permission('foo')
    container = milla.auth.permissions.PermissionContainer(['bar'])
    assert not perm.check(container)

def test_permission_check_container_perm():
    '''Ensure Permission.check returns True for PermissionContainers of Permissions
    '''
    
    perm = milla.auth.permissions.Permission('foo')
    req = milla.auth.permissions.Permission('foo')
    container = milla.auth.permissions.PermissionContainer([perm])
    assert req.check(container)

def test_permission_check_container_perm_false():
    '''Ensure Permission.check returns False for PermissionContainers of Permissions
    '''
    
    perm = milla.auth.permissions.Permission('foo')
    req = milla.auth.permissions.Permission('bar')
    container = milla.auth.permissions.PermissionContainer([perm])
    assert not req.check(container)

def test_permission_container_iter():
    '''Ensure iterating a PermissionContainer yields all permissions
    '''
    
    container = milla.auth.permissions.PermissionContainer(['foo'], ['bar'])
    assert list(container) == ['foo', 'bar']

def test_permission_and():
    '''Ensure AND-ing Permissions returns a PermissionRequirementAll
    '''
    
    perm1 = milla.auth.permissions.Permission('foo')
    perm2 = milla.auth.permissions.Permission('bar')
    req = perm1 & perm2
    assert isinstance(req, milla.auth.permissions.PermissionRequirementAll)
    assert req.requirements == (perm1, perm2)

def test_permission_or():
    '''Ensure OR-ing Permissions returns a PermissionRequirementAny
    '''
    
    perm1 = milla.auth.permissions.Permission('foo')
    perm2 = milla.auth.permissions.Permission('bar')
    req = perm1 | perm2
    assert isinstance(req, milla.auth.permissions.PermissionRequirementAny)
    assert req.requirements == (perm1, perm2)

def test_permission_str():
    '''Ensure calling str on a Permission returns its name
    '''
    
    perm_name = 'foo'
    perm = milla.auth.permissions.Permission(perm_name)
    assert str(perm) == perm_name

def test_permission_eq():
    '''Ensure two Permissions with the same name are equal but not identical
    '''
    
    perm_name = 'foo'
    perm1 = milla.auth.permissions.Permission(perm_name)
    perm2 = milla.auth.permissions.Permission(perm_name)
    assert perm1 == perm2
    assert perm1 is not perm2

def test_permission_check_container_group():
    '''Test group permissions in PermissionContainer objects
    '''
    
    perm = milla.auth.permissions.Permission('foo')
    req = milla.auth.permissions.Permission('foo')
    container = milla.auth.permissions.PermissionContainer([], [perm])
    assert req.check(container)

def test_permissionrequirement_all():
    '''Ensure PermissionRequirementAll requires all listed permissions
    '''
    
    perm1 = milla.auth.permissions.Permission('foo')
    perm2 = milla.auth.permissions.Permission('bar')
    req = milla.auth.permissions.PermissionRequirementAll(perm1, perm2)
    assert req.check(['foo', 'bar'])
    assert not req.check(['foo'])
    assert not req.check(['bar'])
    assert not req.check([])
    assert not req.check(['baz'])

def test_permissionrequirement_any():
    '''Ensure PermissionRequirementAll requires only one permission
    '''
    
    perm1 = milla.auth.permissions.Permission('foo')
    perm2 = milla.auth.permissions.Permission('bar')
    req = milla.auth.permissions.PermissionRequirementAny(perm1, perm2)
    assert req.check(['foo'])
    assert req.check(['bar'])
    assert req.check(['foo', 'bar'])
    assert not req.check([])
    assert not req.check(['baz'])

def test_exception_callable():
    '''Ensure that NotAuthorizedException is a valid controller callable
    '''
    
    exc = milla.auth.NotAuthorized()
    request = milla.Request.blank('/')
    response = exc(request)
    assert isinstance(response, milla.Response)
    assert response.status.startswith('4')

@nose.tools.raises(milla.auth.NotAuthorized)
def test_request_validator_nouser():
    '''Ensure ensure requests without a user attribute raise NotAuthorized
    '''
    
    validator = milla.auth.RequestValidator()
    request = milla.Request.blank('/')
    validator.validate(request)

@nose.tools.raises(milla.auth.NotAuthorized)
def test_request_validator_emptyuser():
    '''Ensure requests with an empty user raise NotAuthorized
    '''
    
    validator = milla.auth.RequestValidator()
    request = milla.Request.blank('/')
    request.user = None
    validator.validate(request)

def test_request_validator_user_noperms():
    '''Ensure user permissions are not checked if no requirement is given
    
    If no ``requirement`` is given to
    :py:meth:`milla.auth.RequestValidator.validate`, then the fact that the
    request's ``user`` attribute doesn't have a ``permissions`` attribute
    shouldn't matter.    
    '''
    
    class User(object):
        pass

    validator = milla.auth.RequestValidator()
    request = milla.Request.blank('/')
    request.user = User()
    validator.validate(request)

@nose.tools.raises(milla.auth.NotAuthorized)
def test_request_validator_missingperms():
    '''Ensure requests whose user has no permissions attribute are invalid
    '''
    
    class User(object):
        pass
    
    validator = milla.auth.RequestValidator()
    request = milla.Request.blank('/')
    request.user = User()
    requirement = milla.auth.permissions.Permission('foo')
    validator.validate(request, requirement)

@nose.tools.raises(milla.auth.NotAuthorized)
def test_request_validator_emptyperms():
    '''Ensure requests whose user has an empty set of permissions are invalid
    '''
    
    class User(object):
        pass
    
    validator = milla.auth.RequestValidator()
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = []
    requirement = milla.auth.permissions.Permission('foo')
    validator.validate(request, requirement)

@nose.tools.raises(milla.auth.NotAuthorized)
def test_request_validator_incorrectperms():
    '''Ensure requests whose user has incorrect permissions raise NotAuthorized
    '''
    
    class User(object):
        pass
    
    validator = milla.auth.RequestValidator()
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['bar']
    requirement = milla.auth.permissions.Permission('foo')
    validator.validate(request, requirement)

def test_request_validator_correctperms():
    '''Ensure requests from users with appropriate permissions are valid
    '''
    
    class User(object):
        pass
    
    validator = milla.auth.RequestValidator()
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['foo']
    requirement = milla.auth.permissions.Permission('foo')
    validator.validate(request, requirement)

def test_find_request_kwarg():
    '''Ensure _find_request finds a request in keyword arguments
    '''
    
    request = milla.Request.blank('/')
    found = milla.auth.decorators._find_request('foo', request=request)
    assert found is request

def test_find_request_arg1():
    '''Ensure _find_request finds a request in position 1
    '''
    
    request = milla.Request.blank('/')
    found = milla.auth.decorators._find_request(request)
    assert found is request

def test_find_request_arg2():
    '''Ensure _find_request finds a request in another position
    '''
    
    request = milla.Request.blank('/')
    found = milla.auth.decorators._find_request('foo', request)
    assert found is request

def test_auth_required_true():
    '''Test the auth_required decorator with a valid user
    '''
    
    class User(object):
        pass
    
    @milla.auth.decorators.auth_required
    def controller(request):
        return 'success'
    
    request = milla.Request.blank('/')
    request.user = User()
    response = controller(request)
    assert response == 'success'

def test_auth_required_false():
    '''Test the auth_required decorator with no user
    '''
    
    @milla.auth.decorators.auth_required
    def controller(request):
        return 'success'

    request = milla.Request.blank('/')
    request.user = None
    response = controller(request)
    assert response != 'success'
    assert response.status.startswith('4')

def test_require_perms_none():
    '''Test the require_perms decorator with no requirement
    '''
    
    class User(object):
        pass
    
    @milla.auth.decorators.require_perms()
    def controller(request):
        return 'success'

    request = milla.Request.blank('/')
    request.user = User()
    response = controller(request)
    assert response == 'success'

def test_require_perms_valid_str():
    '''Test the require_perms decorator with valid permissions as strings
    '''
    
    class User(object):
        pass
    
    @milla.auth.decorators.require_perms('foo')
    def controller(request):
        return 'success'
    
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['foo']
    response = controller(request)
    assert response == 'success'

def test_require_perms_valid_permission():
    '''Test the require_perms decorator with valid permissions as Permissions
    '''
    
    class User(object):
        pass
    
    req = milla.auth.permissions.Permission('foo')
    @milla.auth.decorators.require_perms(req)
    def controller(request):
        return 'success'
    
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['foo']
    response = controller(request)
    assert response == 'success'

def test_require_perms_multi_valid_string():
    '''Test the require_perms decorator with multiple requirements as strings
    '''
    
    class User(object):
        pass
    
    @milla.auth.decorators.require_perms('foo', 'bar')
    def controller(request):
        return 'success'

    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['foo', 'bar']
    response = controller(request)
    assert response == 'success'

def test_require_perms_multi_valid_permission():
    '''Test the require_perms decorator with multiple requirements as Permissions
    '''
    
    class User(object):
        pass
    
    req1 = milla.auth.permissions.Permission('foo')
    req2 = milla.auth.permissions.Permission('bar')
    @milla.auth.decorators.require_perms(req1, req2)
    def controller(request):
        return 'success'

    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['foo', 'bar']
    response = controller(request)
    assert response == 'success'

def test_require_perms_invalid_none():
    '''Test the require_perms decorator with no permissions
    '''
    
    class User(object):
        pass
    
    @milla.auth.decorators.require_perms('foo')
    def controller(request):
        return 'success'
    
    request = milla.Request.blank('/')
    request.user = User()
    response = controller(request)
    assert response != 'success'
    assert response.status.startswith('4')

def test_require_perms_invalid_empty():
    '''Test the require_perms decorator with an empty permissions set
    '''
    
    class User(object):
        pass
    
    @milla.auth.decorators.require_perms('foo')
    def controller(request):
        return 'success'

    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = []
    response = controller(request)
    assert response != 'success'
    assert response.status.startswith('4')

def test_require_perms_invalid_string():
    '''Test the require_perms decorator with invalid permissions as strings
    '''
    
    class User(object):
        pass
    
    @milla.auth.decorators.require_perms('foo')
    def controller(request):
        return 'success'
    
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['bar']
    response = controller(request)
    assert response != 'success'
    assert response.status.startswith('4')

def test_require_perms_invalid_permission():
    '''Test the require_perms decorator with invalid permissions as Permissions
    '''
    
    class User(object):
        pass
    
    req = milla.auth.permissions.Permission('foo')
    @milla.auth.decorators.require_perms(req)
    def controller(request):
        return 'success'
    
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['bar']
    response = controller(request)
    assert response != 'success'
    assert response.status.startswith('4')

def test_require_perms_multi_invalid_string():
    '''Test the require_perms decorator with multiple invalid permissions as strings
    '''
    
    class User(object):
        pass
    
    @milla.auth.decorators.require_perms('foo', 'bar')
    def controller(request):
        return 'success'
    
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['bar']
    response = controller(request)
    assert response != 'success'
    assert response.status.startswith('4')

def test_require_perms_multi_invalid_permission():
    '''Test the require_perms decorator with multiple invalid permissions as Permissions
    '''
    
    class User(object):
        pass
    
    req1 = milla.auth.permissions.Permission('foo')
    req2 = milla.auth.permissions.Permission('foo')
    @milla.auth.decorators.require_perms(req1, req2)
    def controller(request):
        return 'success'
    
    request = milla.Request.blank('/')
    request.user = User()
    request.user.permissions = ['bar']
    response = controller(request)
    assert response != 'success'
    assert response.status.startswith('4')
