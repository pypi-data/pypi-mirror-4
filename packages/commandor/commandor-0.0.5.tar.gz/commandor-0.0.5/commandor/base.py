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
from optparse import Option

from commandor.exceptions import InvalidCommand
from commandor.colors import blue
from commandor.utils import indent


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
                              default = False,
                              help='Show commands')]

    def __init__(self, parser, args=None, options=None):
        self.parser = parser
        self._args = args
        self._options = options
        self._curdir = None

    def add_parser_option(self, option):
        """Add option to parser

        :param option: option object
        """
        self.parser.add_option(option)

    @property
    def args(self):
        """Parsed args property
        """
        return self._args

    @property
    def options(self):
        """Parsed optios property
        """
        return self._options

    def parse_args(self):
        """Parser args and options from parser
        """
        for option in self.default_options:
            self.add_parser_option(option)

        return self.parser.parse_args()

    def process(self):
        """Process parsing
        """

        self._curdir = os.path.abspath(os.path.curdir)
        self._options, self._args = self.parse_args()

        if not self._args:
            self.parser.print_help()

        if self._options.list_commands:
            self.show_commands()

        command, args = self.__class__.find_command(self._args)
        command_instance = command(self.parser, self._args, self._options)
        command_instance.run(self._curdir, *args)


    @classmethod
    def find_command(cls, names):
        """Find command from commands tree

        :param name:
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

    def __init__(self, parser, args=[], options={}):
        self._args = args
        self._options = options
        self.parser = parser

    def register_options(self):
        """Add specifed command options
        to Options Group
        """
        pass

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
    def show(cls, options={}, args=[]):
        """Show command repr

        :param cls: cls object
        :param options: parsed options
        :param args: parsed args
        """
        # Self.Display cls doc
        cls.display(indent("`{}`: {}".format(
            blue(cls.name), cls.help or cls.__doc__.strip()), (cls.level + 1) * 4))

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

    def run(self, *args, **kwargs):
        """Command run loop

        :param \*args: custom args
        :param \*\*: custom kwargs
        """
        raise NotImplementedError, "Add command logic"
