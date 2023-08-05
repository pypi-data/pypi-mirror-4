#!/usr/bin/env python
# -*- coding:  utf-8 -*-
"""
commandor.tests
~~~~~~~~~~~~~~~~~~~~~~~~

Test core utilities

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http://github.com/Lispython/commandor
"""

from optparse import OptionParser, Option
from base import BaseTestCase
from commandor.base import Commandor, Command
from commandor.utils import parse_args


__all__ = 'CoreTestCase',


class CoreTestCase(BaseTestCase):
    """Test core utils of Commandor
    """

    def test_parse_args(self):
        args = "--config=./config.py server start --verbose --processes=8".split()

        self.assertEquals(parse_args(args), (args[:1], args[1:]))

    def test_command(self):
        test_self = self
        command_options = [Option("-v", "--verbose",
                                  action="store_true",
                                  default=False,
                                  help="Switch verbose mode"),
                           Option("-p", "--processes",
                                  default=7,
                                  type="int",
                                  dest="procss",
                                  help="Number of processes")]

        class Commandor2(Commandor):
            """Custom commandor2
            """

        class Server(Command):
            """Server command description
            """
            commandor = Commandor2
            options = command_options

        class Crawler(Command):
            """Crawler command description
            """
            commandor = Commandor2
            options = command_options

            def run(self, verbose, procss):
                test_self.assertTrue(verbose)
                test_self.assertEquals(procss, 9)

        parser = OptionParser(
            usage="%prog [options] <commands>",
            add_help_option=False)

        args = "--verbose --processes=8".split()

        command_instance = Server(parser, args)
        self.assertEquals(command_instance.parser, parser)

        self.assertRaises(NotImplementedError, command_instance.process)

        parsed_options, parsed_args = command_instance.parse_args()

        self.assertEquals(parsed_args, [])
        self.assertEquals(parsed_options.procss, 8)
        self.assertEquals(parsed_options.verbose, True)

        parser = OptionParser(
            usage="%prog [options] <commands>",
            add_help_option=False)

        args = "--verbose --processes=9".split()
        command_instance = Crawler(parser, args)
        command_instance.process()

    def test_commandors(self):
        test_self = self
        command_options = [Option("-v", "--verbose",
                                  action="store_true",
                                  default=False,
                                  help="Switch verbose mode"),
                           Option("-p", "--processes",
                                  default=7,
                                  type="int",
                                  dest="processes",
                                  help="Number of processes")]

        class Commandor1(Commandor):
            """Custom commandor
            """
            test_commandor = False

            def run(self, options, args):
                if options.config == './config_exit.py':
                    return False
                else:
                    test_self.assertEquals(options.config, "./config.py")
                self.test_commandor = True
                return "commandor_name"

        class Server(Command):
            """Command description
            """
            test_server = False
            commandor = Commandor1

            def run(self, options, args):
                test_self.assertFalse(self.test_server)
                return "server_name"

        class Start(Command):
            parent = Server
            test_start = False
            options = command_options

            def run(self, verbose, processes):
                test_self.assertTrue(verbose)
                test_self.assertEquals(processes, 10)
                test_self.assertFalse(self.test_start)
                return "start_name"

        parser = OptionParser(
            usage="%prog [options] <commands>",
            add_help_option=False)

        commandor_options = [Option('-c', '--config',
                                    metavar="FILE",
                                    help='Commandor configuration file')]

        commandor_args = "--config=./config.py server start --verbose --processes=10".split()

        commandor = Commandor1(parser, args=commandor_args, options=commandor_options)

        commandor.add_parser_options()
        parsed_options, parsed_args = commandor.parse_args(["--config=./config.py"])

        self.assertEquals(parsed_options.config, "./config.py")
        self.assertEquals(parsed_args, [])

        command, args = commandor.__class__.find_command(['sserver'])
        self.assertEquals(command, commandor.__class__)
        self.assertEquals(args, ['sserver'])

        command, args = commandor.__class__.find_command(['server'])
        self.assertEquals(command, Server)
        self.assertEquals(args, [])

        parser = OptionParser(
            usage="%prog [options] <commands>",
            add_help_option=False)

        commandor = Commandor1(parser, args=commandor_args,
                               options=commandor_options)

        self.assertEquals(commandor.process(), "start_name")

        # Test commandor run
        commandor_args = "--config=./config_exit.py".split()

        parser = OptionParser(
            usage="%prog [options] <commands>",
            add_help_option=False)

        commandor = Commandor1(parser, args=commandor_args,
                               options=commandor_options)
        self.assertEquals(commandor.process(), False)
