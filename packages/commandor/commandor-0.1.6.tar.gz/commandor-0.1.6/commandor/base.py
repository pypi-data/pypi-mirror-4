#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
Commandor
~~~~~~~~

A system integration framework for configuration management
to you infrastructure

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http://github.com/Lispython/commandor
"""

import sys
import os.path
from optparse import Option, OptionParser as BaseOptionParser

from commandor.exceptions import (InvalidCommand,
                                  InvalidScriptOption, InvalidCommandOption)
from commandor.colors import blue, red
from commandor.utils import indent, parse_args
from commandor.compat import with_metaclass


__all__ = 'Command', 'Commandor', 'OptionParser'

class OptionParser(BaseOptionParser):
    def exit(self, status=0, msg=None):
        sys.exit(status)

    def format_help(self, formatter=None):
        if formatter is None:
            formatter = self.formatter
        result = []
        if self.description:
            result.append(self.format_description(formatter) + "\n")
        result.append(self.format_option_help(formatter))
        result.append(self.format_epilog(formatter))
        return "".join(result)


class Mixin(object):
    """Helpers for manage command
    """

    @classmethod
    def lookup_command(cls, name):
        """Search commands for command

        :param name: command name
        """
        if name not in cls.commands.keys():
            raise InvalidCommand("{0} not a valid command".format(name))
        return cls.commands[name]

    @staticmethod
    def exit(status=0):
        """Exit
        """
        sys.exit(status)

    @staticmethod
    def display(s, c=None):
        """Display input string `s`
        """
        if c:
            # Display colorized
            print(c(s))
        else:
            print(s)

    def error(self, s):
        self.display(s, red)

    def abort(self, s):
        """Display and exit
        """
        self.display(s)
        self.exit()


class CommandMetaClass(type):
    """Command meta class
    """
    def __new__(mcs, name, bases, params):
        cls = super(CommandMetaClass, mcs).__new__(mcs, name, bases, params)

        # Re init commands property
        if cls.__name__ == "NewBase":
            return cls

        cls.commands = {}

        if cls.parent:
            if name.lower().startswith(cls.parent.name.lower()):
                cls.name = name.lower()[len(cls.parent.name.lower()):]
            else:
                cls.name = name.lower()
            cls.parent.add_command(cls)
            cls.level = cls.parent.level + 1
            if cls.parent.tree:
                cls.tree = cls.parent.tree + [cls.parent]
            else:
                cls.tree = [cls.parent]
        else:
            cls.name = name.lower()

        if hasattr(cls, 'commandor'):
            cls.commandor.register_command(cls)

        return cls

CommandBase = with_metaclass(CommandMetaClass)


class CommandorMetaClass(type):
    """Commandor Meta class
    """
    def __new__(mcs, name, bases, params):
        cls = super(CommandorMetaClass, mcs).__new__(mcs, name, bases, params)

        # Add commands in meta class
        # because we don't wont share object
        # between Commandor subclasses
        cls.commands = {}
        return cls

CommandorBase = with_metaclass(CommandorMetaClass)

class Commandor(CommandorBase, Mixin):
    """Command manager
    """
    __metaclass__ = CommandorMetaClass
    commands = {}
    initialized_commands = {}
    default_options = [Option('-L', '--list-commands',
                              action='store_true',
                              default=False,
                              help='Show commands'),
                       Option('-h', '--help',
                              action='store_true',
                              default=False,
                              help='Show help for script')]

    def __init__(self, parser, args=sys.argv[1:], options=[]):
        """Initialize commandor

        :param parser: :class:`~optparse.OptionParse` object
        :param args: list or script arguments
        :param options: list of additional :class:`~optparse.Option` objects
        """
        self.parser = parser
        self._args = args
        self._options = options
        self._curdir = None

        # Options after args_parse
        self._parsed_options = None

    def add_parser_options(self):
        """Add options to parser
        """
        for option in self.default_options + self._options:
            self.add_parser_option(option)

    def add_parser_option(self, option):
        """Add option to parser

        :param option: option object
        """
        self.parser.add_option(option)

    def parse_args(self, args=[]):
        """Parser args and options from parser
        :param args: script args, exclude commands and commands args
        :return: tuple of options and empty args
        """
        try:
            return self.parser.parse_args(args)
        except SystemExit:
            raise InvalidScriptOption(sys.exc_info()[0])

    def run(self, options, args, **kwargs):
        """Execute

        :param options: commandor options
        :param args: list of commandor args
        :returns: return True for continue
        """

        if options.list_commands:
            self.parser.print_help()
            self.show_commands(args)
            # System exit

        ## if isinstance(args, (list, tuple)) and \
        ##        not any([arg for arg in args if not arg.startswith('-')]):
        ##     self.parser.print_help()

        return True

    def process(self):
        """Process parsing
        """

        # Configure self.parser options
        self.add_parser_options()

        commandor_args, commands = parse_args(self._args)

        self._curdir = os.path.abspath(os.path.curdir)


        # Commandor parsed options and args (that empty list)
        # Because all args separated into commands_args
        self._parsed_options, _ = self.parse_args(commandor_args)

        res = self.run(self._parsed_options, commands)

        # If need run only commandor without subcommands
        if res is None:
            return None

        command, command_args = self.__class__.find_command(commands)

        if issubclass(command, Commandor):
            # if subcommands not specified, show help and exit
            self.parser.print_help()
            self.show_commands(commands)
            self.exit()
        else:
            command_instance = command(cur_dir=self._curdir,
                                       args=command_args, commandor_res=res)
        return command_instance.process()

    @classmethod
    def find_command(cls, names):
        """Find command from commands tree

        :pa options={}, ram cls:
        :param names:
        """
        command = cls
        try:
            for name in names[:]:
                command = command.lookup_command(name)
                names.pop(0)
        except InvalidCommand:
            # Parse arguments
            pass
        return command, names

    def show_commands(self, args):
        """Show registered commands

        :param args: list of command params
        """
        command = self
        if args:
            command, names = self.__class__.find_command(args)
            self.display("Subcommands list for {0}".format('.'.join(names)))
            self.exit()

        self.display("\nCommands list:")

        for command in self.commands.values():
            command.show(args)
        self.exit()

    @classmethod
    def register_command(cls, command):
        """Register core commands in commandor

        :param cls: commandor class
        :param command: command to register
        """
        cls.commands[command.name] = command


class Command(CommandBase, Mixin):
    """Single console command

    :attribute name: command name
    :attribute command: dict of commands
    :attribute parent: parent command
    """

    __metaclass__ = CommandMetaClass

    tree = []
    level = 0
    parent = None
    name = 'command'
    options = []
    default_options = [
        Option(None, '--help',
               action='store_true',
               default=False,
               help='Show help for command')]

    help = None

    def __init__(self, parser=None, args=[], cur_dir=None, commandor_res=None):
        self._args = args
        self.parser = parser
        self._cur_dir = cur_dir
        self._commandor_res = commandor_res

    def initialize_parser(self):
        """Create :class:`optparse.OptionParse`
        """
        if not self.parser:
            self.parser = OptionParser(
                usage="{0} [options]".format(self.__class__.__name__),
                add_help_option=False)

    def register_option(self, option):
        """Register :class:`optparse.Option` in `self.parser`

        :param option: :class:`optparse.Option` object
        """
        self.parser.add_option(option)

    def register_options(self):
        """Add specifed command options
        to Options Group
        """
        for option in self.default_options + self.options:
            self.register_option(option)

    @classmethod
    def print_commands(cls, args, base_ident=None):
        """Display command commands

        :param options: options dict
        :param args: script arguments
        """
        for name, command in cls.commands.items():
            cls.print_command(name, args, base_ident)

    @classmethod
    def print_command(cls, name, args=[], base_ident=None):
        """Pretty print command

        :param name: command name
        """
        command = cls.lookup_command(name)
        command.show(args, base_ident)


    def print_command_help(self):
        """Print command help and exit
        """
        self.display(self.__class__.usage())
        self.display(self.parser.format_help())

        # Display subcommands if exists
        if self.commands:
            self.display("Subcommands list for {0}".format(self.name))
            self.__class__.print_commands([], base_ident=1)

    @classmethod
    def usage(cls):
        """Print command usage
        """
        return "Usage: {0} [options] {1}\n".format(
            sys.argv[0], ' '.join([x.name for x in cls.tree] + [cls.name]))


    @classmethod
    def show(cls, args=[], base_ident=None):
        """Show command repr

        :param cls: cls object
        :param options: parsed options
        :param args: parsed args
        """
        # Self.Display cls doc
        cls.display(indent("`{0}`: {1}".format(
            blue(cls.name), cls.help or (cls.__doc__.strip() if cls.__doc__ else 'No doc')),
                           (cls.level + 1 if base_ident is None else base_ident) * 4))

        if cls.commands:
            cls.print_commands(args, base_ident if base_ident is None else base_ident + 1 )

    @classmethod
    def add_command(cls, command):
        """Add commands to class

        :param cls: add command to cls
        :param command: command object
        """
        cls.commands[command.name] = command
        return True

    def configure(self):
        """Configure command before execute
        """
        self.initialize_parser()

        self.register_options()

    def parse_args(self):
        """Parse arguments
        :return: tuple of options and args
        """
        try:
            return self.parser.parse_args(self._args)
        except SystemExit:
            raise InvalidCommandOption(sys.exc_info()[1])

    def process(self):
        """Execute command
        """
        self.configure()

        options, args = self.parse_args()
        d = dict([(x.dest, getattr(options, x.dest, None))
                  for x in self.parser.option_list])
        if options.help:
            self.print_command_help()
            self.exit()
        del d["help"]

        return self.run(**d)

    def run(self, *args, **kwargs):
        """Command run loop

        :param \*args: custom args
        :param \*\*: custom kwargs
        """
        raise NotImplementedError("Add command logic")
