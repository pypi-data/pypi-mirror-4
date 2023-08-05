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
'''URL Dispatching

:Created: Mar 26, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''

from milla.dispatch import UnresolvedPath

class Traverser(object):
    '''Default URL dispatcher
    
    :param root: The root object at which lookup will begin
    
    The default URL dispatcher uses object attribute traversal to
    locate a handler for a given path. For example, consider the
    following class::
    
       class Root(object):
           
           def foo(self):
               return 'Hello, world!'
    
    The path ``/foo`` would resolve to the ``foo`` method of the
    ``Root`` class.
    
    If a path cannot be resolved, :py:exc:`UnresolvedPath` will be
    raised.
    '''
    
    def __init__(self, root):
        self.root = root
    
    def resolve(self, path_info):
        '''Find a handler given a path
        
        :param path_info: Path for which to find a handler
        :returns: A handler callable
        '''
        
        def walk_path(handler, parts):
            if not parts or not parts[0]:
                # No more parts, or the last part is blank, we're done
                return handler
            try:
                return walk_path(getattr(handler, parts[0]), parts[1:])
            except AttributeError:
                # The handler doesn't have an attribute with the current
                # segment value, try the default
                try:
                    return handler.default
                except AttributeError:
                    # No default either, can't resolve
                    raise UnresolvedPath
        
        # Strip the leading slash and split the path
        split_path = path_info.lstrip('/').split('/')
        
        handler = walk_path(self.root, split_path)
        return handler