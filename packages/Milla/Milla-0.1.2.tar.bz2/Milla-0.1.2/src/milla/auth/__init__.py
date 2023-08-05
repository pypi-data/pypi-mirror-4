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
'''Request authorization

:Created: Apr 5, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''

class NotAuthorized(Exception):
    '''Base class for unauthorized exceptions
    
    This class is both an exception and a controller callable. If the
    request validator raises an instance of this class, it will be
    called and the resulting value will become the HTTP response. The
    default implementation simply returns HTTP status 403 and a simple
    body containing the exception message.
    '''

    def __call__(self, request, *args, **kwargs):
        '''Return a response indicating the request is not authorized

        :param request: WebOb Request instance for the current request
        
        All other arguments and keywords are ignored.
        '''
        
        response = request.ResponseClass(unicode(self))
        response.status_int = 403
        return response

class RequestValidator(object):
    '''Base class for request validators
    
    A request validator is a class that exposes a ``validate`` method,
    which accepts an instance of :py:class:`webob.Request` and an
    optional ``requirement``. The ``validate`` method should return
    ``None`` on successful validation, or raise an instance of
    :py:exc:`NotAuthorized` on failure. The base implementation will
    raise an instance of the exception specified by
    :py:attr:`exc_class`, which defaults to :py:class`NotAuthorized`.
    
    To customize the response to unauthorized requests, it is
    sufficient to subclass :py:class:`NotAuthorized`,  override its
    :py:meth:`~NotAuthorized.__call__` method, and specify the class
    in :py:attr:`exc_class`.
    '''

    #: Exception class to raise if the request is unauthorized
    exc_class = NotAuthorized

    def validate(self, request, requirement=None):
        '''Validates a request
        
        :param request: The request to validate. Should be an instance
           of :py:class:`webob.Request`.
        :param requirement: (Optional) A requirement to check. Should be
           an instance of :py:class:`~milla.auth.permissions.Permission`
           or :py:class:`~milla.auth.permissions.PermissionRequirement`,
           or some other class with a ``check`` method that accepts a
           sequence of permissions.
        
        The base implementation will perform authorization in the
        following way:
        
        1. Does the ``request`` have a ``user`` attribute? If not,
           raise :py:exc:`NotAuthorized`.
        2. Is the truth value of ``request.user`` true? If not, raise
           :py:exc:`NotAuthorized`.
        3. Does the ``request.user`` object have a ``permissions``
           attribute? If not, raise :py:exc:`NotAuthorized`.
        4. Do the user's permissions meet the requirements? If not,
           raise :py:exc:`NotAuthorized`.
        
        If none of the above steps raised an exception, the method will
        return ``None``, indicating that the validation was successful.
        
        .. note:: WebOb Request instances do not have a ``user``
           attribute by default. You will need to supply this yourself,
           i.e. in a WSGI middleware or in the ``__before__`` method of
           your controller class.
        '''
        
        try:
            user = request.user
        except AttributeError:
            # No user associated with the request at all
            raise self.exc_class('Request has no user')

        if not user:
            raise self.exc_class('Anonymous not allowed')

        if requirement:
            try:
                user_perms = user.permissions
            except AttributeError:
                raise self.exc_class('User has no permissions')

            if not requirement.check(user_perms):
                raise self.exc_class('User does not have required permissions')
