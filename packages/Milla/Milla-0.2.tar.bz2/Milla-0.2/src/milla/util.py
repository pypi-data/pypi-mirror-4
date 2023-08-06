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
'''Convenience utility functions

:Created: Mar 30, 2011
:Author: dustin
'''

from wsgiref.handlers import format_date_time
import datetime
import time
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

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


def http_date(date):
    '''Format a datetime object as a string in RFC 1123 format

    This function returns a string representing the date according to
    RFC 1123. The string returned will always be in English, as
    required by the specification.

    :param date: A :py:class:`datetime.datetime` object
    :return: RFC 1123-formatted string
    '''

    stamp = time.mktime(date.timetuple())
    return format_date_time(stamp)


def read_config(filename, defaults=None):
    '''Parse an ini file into a nested dictionary

    :param string filename: Path to the ini file to read
    :param dict defaults: (Optional) A mapping of default values that can be
       used for interpolation when reading the configuration file
    :returns: A dictionary whose keys correspond to the section and
       option, joined with a dot character (.)

    For example, consider the following ini file::

        [xmen]
        storm = Ororo Monroe
        cyclops = Scott Summers

        [avengers]
        hulk = Bruce Banner
        iron_man = Tony Stark

    The resulting dictionary would look like this::

        {
            'xmen.storm': 'Ororo Monroe',
            'xmen.cyclops': 'Scott Summers',
            'avengers.hulk': 'Bruce Banner',
            'avengers.iron_man': 'Tony Stark',
        }

    Thus, the option values for any section can be obtained as follows::

        config['xmen.storm']

    This dictionary can be used to configure an :py:class:`~milla.Application`
    instance by using the ``update`` method::

        config = milla.util.read_config('superheros.ini')
        app = milla.Application(router)
        app.config.update(config)
    '''

    with open(filename) as f:
        # ConfigParser API changed in Python 3.2
        if hasattr(configparser.ConfigParser, 'read_file'):
            cparser = configparser.ConfigParser(defaults)
            cparser.read_file(f)
        else:
            cparser = configparser.SafeConfigParser(defaults)
            cparser.readfp(f)

    config = {}
    for section in cparser.sections():
        for option in cparser.options(section):
            config['.'.join((section, option))] = cparser.get(section, option)
    return config
