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
'''Stub controller classes

These classes can be used as base classes for controllers. While any
callable can technically be a controller, using a class that inherits
from one or more of these classes can make things significantly easier.

:Created: Mar 27, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''

import milla
import pkg_resources


class Controller(object):
    '''The base controller class

    This class simply provides empty ``__before__`` and ``__after__``
    methods to facilitate cooperative multiple inheritance.
    '''

    def __before__(self, request):
        pass

    def __after__(self, request):
        pass


class FaviconController(Controller):
    '''A controller for the "favicon"

    This controller is specifically suited to serve a site "favicon" or
    bookmark icon. By default, it will serve the *Milla* icon, but you
    can pass an alternate filename to the constructor.

    :param icon: Path to an icon to serve
    :param content_type: Internet media type describing the type of image
       used as the favicon, defaults to 'image/x-icon' (Windows ICO format)
    '''

    def __init__(self, icon=None, content_type='image/x-icon'):
        if icon:
            try:
                self.icon = open(icon)
            except (IOError, OSError):
                self.icon = None
        else:
            try:
                self.icon = pkg_resources.resource_stream('milla', 'milla.ico')
            except IOError:
                self.icon = None
        self.content_type = content_type

    def __call__(self, request):
        if not self.icon:
            raise milla.HTTPNotFound
        response = milla.Response()
        response.app_iter = self.icon
        response.headers['Content-Type'] = self.content_type
        return response
