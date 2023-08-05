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

from app import *
from webob.exc import *
from webob.request import *
from webob.response import *
from auth.decorators import *

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
