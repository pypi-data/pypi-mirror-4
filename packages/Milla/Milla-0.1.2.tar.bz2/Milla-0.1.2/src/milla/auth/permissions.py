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
'''Classes for calculating user permissions

Examples::

    >>> req = Permission('foo') & Permission('bar')
    >>> req.check(PermissionContainer(['foo', 'baz'], ['bar']))
    True
    
    >>> req = Permission('login')
    >>> req.check(['login'])
    True
    
    >>> req = Permission('login') | Permission('admin')
    >>> req.check(['none'])
    False
'''

class PermissionContainer(object):
    '''Container object for user and group permissions
    
    :param list user_perms: List of permissions held by the user itself
    :param list group_perms: List of permissions held by the groups to
       which the user belongs
    
    Iterating over :py:class:`PermissionContainer` objects results in
    a flattened representation of all permissions.
    '''
    
    def __init__(self, user_perms=[], group_perms=[]):
        self._user_perms = user_perms
        self._group_perms = group_perms
    
    def __iter__(self):
        for perm in self._user_perms:
            yield perm
        for perm in self._group_perms:
            yield perm
    
    def __contains__(self, perm):
        return perm in self._user_perms or perm in self._group_perms
            

class BasePermission(object):
    '''Base class for permissions and requirements
    
    Complex permission requirements can be created using the bitwise
    ``and`` and ``or`` operators::
    
        login_and_view = Permission('login') & Permission('view')
        admin_or_root = Permission('admin') | Permission('root')
        
        complex = Permission('login') & Permission('view') | Permission('admin')
    '''
    
    def __and__(self, other):
        assert isinstance(other, BasePermission)
        return PermissionRequirementAll(self, other)
    
    def __or__(self, other):
        assert isinstance(other, BasePermission)
        return PermissionRequirementAny(self, other)

class Permission(BasePermission):
    '''Simple permission implementation
    
    :param str name: Name of the permission
    
    Permissions must implement a ``check`` method that accepts an
    iterable and returns ``True`` if the permission is present or
    ``False`` otherwise.
    '''
    
    def __init__(self, name):
        self.name = name
    
    def __unicode__(self):
        if isinstance(self.name, unicode):
            return self.name
        else:
            return self.name.decode('utf-8')
    
    def __str__(self):
        if isinstance(self.name, str):
            return self.name
        else:
            return self.name.encode('utf-8')

    def __eq__(self, other):
        return self is other or str(self) == str(other)

    def check(self, perms):
        '''Check if the permission is held
        
        This method can be overridden to provide more robust
        support, but this implementation is simple::
        
           return self in perms
        '''
        
        return self in perms

class PermissionRequirement(BasePermission):
    '''Base class for complex permission requirements'''
    
    def __init__(self, *requirements):
        self.requirements = requirements
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    
class PermissionRequirementAll(PermissionRequirement):
    '''Complex permission requirement needing all given permissions'''
    
    def check(self, perms):
        for req in self.requirements:
            if not req.check(perms):
                return False
        return True

class PermissionRequirementAny(PermissionRequirement):
    '''Complex permission requirement needing any given permissions'''
    
    def check(self, perms):
        for req in self.requirements:
            if req.check(perms):
                return True
        return False
