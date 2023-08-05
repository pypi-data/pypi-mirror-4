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
from optparse import Option, OptionParser

from commandor.exceptions import InvalidCommand
from commandor.colors import blue
from commandor.utils import indent, parse_args


__all__ = 'Command', 'Commandor'


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
    def exit():
        """Exit
        """
        print("Exit from loop")
        sys.exit(0)

    @staticmethod
    def display(s):
        """Display input string `s`
        """
        print(s)

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

        cls.commands = {}

        if cls.parent:
            if name.lower().startswith(cls.parent.name.lower()):
                cls.name = name.lower()[len(cls.parent.name.lower()):]
            else:
                cls.name = name.lower()
            cls.parent.add_command(cls)
            cls.level = cls.parent.level + 1
        else:
            cls.name = name.lower()

        if hasattr(cls, 'commandor'):
            cls.commandor.register_command(cls)

        return cls


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


class Commandor(Mixin):
    """Command manager
    """
    __metaclass__ = CommandorMetaClass
    commands = {}
    initialized_commands = {}
    default_options = [Option('-L', '--list-commands',
                              action='store_true',
                              default=False,
                              help='Show commands')]

    def __init__(self, parser, args=[], options=[]):
        """Initialize commandor

        :param parser: :class:`~optparse.OptionParse` object
        :param args: list or script arguments
        :param options: list of additional :class:`~optparse.Option` objects
        """
        self.parser = parser
        self._args = args or sys.argv[1:]
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
        return self.parser.parse_args(args or self._args)

    def run(self, options, args):
        """Execute

        :param options: commandor options
        :param args: list of commandor args
        :returns: return True for continue
        """

        if options.list_commands:
            self.show_commands()

        if isinstance(args, (list, tuple)) and\
               not any([arg for arg in args if not arg.startswith('-')]):
            self.parser.print_help()

        return False

    def process(self):
        """Process parsing
        """
        args, commands_args = parse_args(self._args)

        self._curdir = os.path.abspath(os.path.curdir)

        self.add_parser_options()

        self._parsed_options, _ = self.parse_args(args)

        res = self.run(self._parsed_options, commands_args)

        if not res:
            return res

        command, args = self.__class__.find_command(commands_args)
        command_instance = command(cur_dir=self._curdir, args=args, commandor_res=res)
        return command_instance.process()

    @classmethod
    def find_command(cls, names):
        """Find command from commands tree

        :param cls:
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

    def show_commands(self):
        """Show registered commands
        """
        command = self
        if self._args:
            command, names = self.__class__.find_command(self._args)
            self.display("Subcommands list for {}".format('.'.join(names)))
            command.show(self._options, self._args)
            self.exit()

        self.display("\nCommands list:")

        for command in self.commands.values():
            command.show(self._options, self._args)
        self.exit()

    @classmethod
    def register_command(cls, command):
        """Register core commands in commandor

        :param cls: commandor class
        :param command: command to register
        """
        cls.commands[command.name] = command


class Command(Mixin):
    """Single console command

    :attribute name: command name
    :attribute command: dict of commands
    :attribute parent: parent command
    """

    __metaclass__ = CommandMetaClass

    level = 0
    parent = None
    name = 'command'
    options = []

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
        for option in self.options:
            self.register_option(option)

    @classmethod
    def print_commands(cls, options, args):
        """Display command commands

        :param options: options dict
        :param args: script arguments
        """
        for name, command in cls.commands.items():
            cls.print_command(name, options, args)

    @classmethod
    def print_command(cls, name, options={}, args=[]):
        """Pretty print command

        :param name: command name
        """
        command = cls.lookup_command(name)
        command.show(options, args)

    @classmethod
    def show(cls, options=[], args=[]):
        """Show command repr

        :param cls: cls object
        :param options: parsed options
        :param args: parsed args
        """
        # Self.Display cls doc
        cls.display(indent("`{0}`: {1}".format(
            blue(cls.name), cls.help or cls.__doc__.strip()),
                           (cls.level + 1) * 4))

        if cls.commands:
            cls.print_commands(options, args)

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
        return self.parser.parse_args(self._args)

    def process(self):
        """Execute command
        """
        self.configure()

        options, args = self.parse_args()
        d = dict([(x.dest, getattr(options, x.dest, None))
                  for x in self.parser.option_list])
        return self.run(**d)

    def run(self, *args, **kwargs):
        """Command run loop

        :param \*args: custom args
        :param \*\*: custom kwargs
        """
        raise NotImplementedError("Add command logic")
