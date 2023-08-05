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
'''Module milla.cli

Please give me a docstring!

:Created: May 30, 2011
:Author: dustin
:Updated: $Date$
:Updater: $Author$
'''
import argparse
import pkg_resources
import warnings

class CommandWarning(UserWarning):
    '''A warning raised when a command cannot be loaded or used'''
    

class CommandLineInterface(object):
    '''Wrapper class for the Milla CLI'''
    
    PROGNAME = 'milla-cli'
    EPGROUP = 'milla.command'

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog=self.PROGNAME)
        subparsers = None
        subcmds = pkg_resources.iter_entry_points(self.EPGROUP)
        for cmd in subcmds:
            try:
                Command = cmd.load()
            except Exception as e:
                warnings.warn("Unable to load command from entry point named "
                              "'{epname}': {e}".format(
                                  epname=cmd,
                                  e=e,
                              ), CommandWarning)
                continue

            if not hasattr(Command, 'name') or not Command.name:
                warnings.warn("Command '{cmd}' from '{mod}' does not have a "
                              "name and cannot be used".format(
                                  cmd=Command.__name__,
                                  mod=Command.__module__
                              ), CommandWarning)
                continue

            if not subparsers:
                subparsers = self.parser.add_subparsers()
            subcmd = subparsers.add_parser(Command.name, *Command.parser_args,
                                           **Command.parser_kwargs)
            Command.setup_args(subcmd)
            subcmd.set_defaults(func=Command())


class Command(object):
    '''Base class for "commands"
    
    To create a command, subclass this class and override the following
    attributes:
    
    * ``name`` -- Name of the subcommand
    * ``parser_args`` -- arguments to pass to ``add_parser`` when
      creating the ArgumentParser for the command
    * ``parser_kwargs`` -- keywords to pass to ``add_parser``
    * ``setup_args()`` -- Class method called to add arguments, etc. to
      the command subparser.
    '''

    #: Tuple of arguments to pass to the ArgumentParser constructor
    parser_args = ()
    #: Dict of keywords to pass to the ArgumentParser constructor
    parser_kwargs = {}
    
    @classmethod
    def setup_args(cls, parser):
        '''Add arguments, etc to the command subparser
        
        Override this method to add arguments, options, etc. to the
        subparser for the command. The default implementation does
        not add anything.
        
        :param parser: An instance of ``ArgumentParser`` for the
           ``milla-cli`` subcommand
        '''
        
        pass

def main():
    '''Entry point for the ``milla-cli`` console script'''
    
    cli = CommandLineInterface()
    args = cli.parser.parse_args()
    func = args.func
    del args.func
    func.args = args
    func()
