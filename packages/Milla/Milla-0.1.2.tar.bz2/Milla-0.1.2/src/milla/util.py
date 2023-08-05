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
'''Module milla.uti

Please give me a docstring!

:Created: Mar 30, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''

def asbool(val):
    '''Test a value for truth
    
    Returns ``False`` values evaluating as false, such as the integer
    ``0`` or ``None``, and for the following strings, irrespective of
    letter case:
    
    * false
    * no
    * f
    * n
    * off
    * 0
    
    Returns ``True`` for all other values.
    '''
    
    if not val:
        return False
    try:
        val = val.lower()
    except AttributeError:
        pass
    if val in ('false', 'no', 'f', 'n', 'off', '0'):
        return False
    return True