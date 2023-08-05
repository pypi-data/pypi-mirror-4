# Copyright 2012 Loop Lab
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


__version__ = '0.1.4'
__project_url__ = 'https://github.com/looplab/skal'


import sys
import argparse
import inspect
import types


class SkalApp(object):
    """A base class for command-subcommand apps

    This class is meant to be used either as a base class for a complete
    application or on its own loading the application commands from modules and
    packages. See README.md for usage info.

    """
    def __init__(self,
                 description=None,
                 version=None,
                 command_modules=[],
                 subcommand_modules=[]):
        """Creates the argparser using metadata from decorators

        Keyword arguments:
        description        -- The main help text, if None the class docstring
        version            -- The version string of the app
        command_modules    -- List, functions from each module will be commands
        subcommand_modules -- List, each module will be a subcommand

        """
        # Description and version
        if self.__class__ is SkalApp:
            if description:
                description = inspect.cleandoc(description)
        else:
            description = inspect.getdoc(self)
            module = sys.modules[self.__class__.__module__]
            if hasattr(module, '__version__'):
                version = str(module.__version__)
        if not description:
            sys.stderr.write('Warning: no main documentation\n')
            description = ""

        # Add the main parser
        self.__parser = argparse.ArgumentParser(
            description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter)
        self.__subparser = self.__parser.add_subparsers()
        if version:
            self.__parser.add_argument('--version', action='version',
                                       version=('%(prog)s v' + version))

        # Sub class
        if hasattr(self.__class__, '__args__'):
            _add_arguments(self.__class__.__args__, self.__parser)
        methods = inspect.getmembers(self.__class__, inspect.ismethod)
        for name, method in methods:
            bound_method = types.MethodType(method, self, self.__class__)
            _add_command(bound_method, self.__subparser)

        # Modules, as commands
        for name in command_modules:
            module = _import_module(name)
            if not module:
                break
            _add_commands_from_module(module, self.__parser, self.__subparser)

        # Modules, as subcommands
        for name in subcommand_modules:
            module = _import_module(name)
            if not module:
                break
            module_parser, module_subparser = _add_subparser(
                module, self.__subparser)
            _add_commands_from_module(module, module_parser, module_subparser)

        # Package, as commands

        # Package, as subcommands

    def run(self, args=None):
        """Applicatin starting point.

        This will run the associated method/function/module or print a help
        list if it's an unknown keyword or the syntax is incorrect.

        Keyword arguments:
        args -- Custom application arguments (default sys.argv)

        """
        self.args = self.__parser.parse_args(args=args)
        if 'cmd' in self.args:
            if inspect.isfunction(self.args.cmd):
                self.args.cmd(args=self.args)
            else:
                self.args.cmd()


def command(func_or_args=None):
    """Decorator to tell Skal that the method/function is a command.

    """
    def decorator(f):
        f.__args__ = args
        return f
    if type(func_or_args) == type(decorator):
        args = {}
        return decorator(func_or_args)
    args = func_or_args
    return decorator


def default(f):
    """Decorator to tell Skal that the method/function is the default.

    """
    raise NotImplementedError


def _add_arguments(args, parser):
    for k in args:
        arg = []
        if type(k) == str:
            arg.append(k)
        elif type(k) == tuple:
            short, full = k
            if type(short) == str:
                arg.append(short)
            if type(full) == str:
                arg.append(full)
        options = args[k]
        parser.add_argument(*arg, **options)


def _add_command(function, parent):
    if hasattr(function, '__args__'):
        help, desc = _extract_doc(function)
        if function.__name__ in parent._name_parser_map:
            sys.stderr.write(
                'Warning: ignoring duplicate command "%s" in %s\n' % (
                function.__name__, inspect.getfile(function)))
            return
        parser = parent.add_parser(
            function.__name__,
            description=desc,
            help=help)
        _add_arguments(function.__args__, parser)
        parser.set_defaults(cmd=function)


def _add_subparser(module, parent):
    help, desc = _extract_doc(module)
    parser = parent.add_parser(
        module.__name__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
        help=help)
    subparser = parser.add_subparsers()
    return parser, subparser


def _import_module(name):
    module = None
    try:
        module = __import__(name)
    except SyntaxError as e:
        sys.stderr.write('Warning: syntax error in "%s"\n' % e.filename)
        sys.stderr.write(e)
        sys.stderr.write('\n')
    return module


def _add_commands_from_module(module, parser, subparser):
    if hasattr(module, '__args__'):
        _add_arguments(module.__args__, parser)
    functions = inspect.getmembers(module, inspect.isfunction)
    for name, function in functions:
        _add_command(function, subparser)


def _extract_doc(item):
    desc = inspect.getdoc(item)
    if not desc:
        sys.stderr.write('Warning: no documentation for "%s" in %s\n' % (
            item.__name__, inspect.getfile(item)))
        desc = ''
        help = ''
    else:
        help = desc.split('\n')[0]
    return help, desc
