#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
commandor.examples.main
~~~~~~~~~~~~~~~~~~~~~~~

Example of commandor usage

:copyright: (c) 2012 by Alexandr Lispython (alex@obout.ru).
:license: BSD, see LICENSE for more details.
:github: http://github.com/Lispython/commandor
"""

from optparse import OptionParser, Option


from commandor import Command, Commandor


class CustomCommandor(Commandor):
    """Commandor Customization
    """

class CustomCommandor2(Commandor):
    """Commandor Customization2
    """

class Server(Command):
    """Server management
    """
    commandor = CustomCommandor

class ServerList(Command):
    """Show available servers
    """
    parent = Server


class ServerStart(Command):
    """Start given server
    """
    parent = Server

    options = [
        Option("-P", "--port",
               metavar="int",
               default=8891,
               help="Port to run http server"),
        Option("-r", "--reload",
               action="store_true",
               dest="reload",
               default=False,
               help="Auto realod source on changes"),
        Option("-H", "--host",
               metavar="str",
               default="127.0.0.1",
               help="Port for server"),
        Option("-l", "--logging",
               metavar="str",
               default="none",
               help="Log level")]



class ServerStop(Command):
    """Stop given server
    """
    parent = Server


class Cluster(Command):
    """Cluster namagement
    """
    commandor = CustomCommandor

    def run(self, *args,**kwargs):
        self.display(args)
        self.display("Do something")


class ClusterList(Command):
    """Show cluster list
    """
    parent = Cluster


class ClusterDestroy(Command):
    """Destroy cluster
    """
    parent = Cluster

class ClusterInfo(Command):
    """Show cluster info
    """
    parent = Cluster

class RootLevel(Command):
    """Root level command
    """
    commandor = CustomCommandor

class Level1(Command):
    """Level1 command
    """
    parent = RootLevel

class Level2(Command):
    """Level2 command
    """
    parent = Level1

class Level3(Command):
    """Level3
    """
    parent = Level2

class Level4(Command):
    """Level4
    """
    parent = Level3

def main():
    """Main execution loop
    """

    parser = OptionParser(
        usage="%prog [options] <commands>",
        add_help_option=False)

    parser.add_option('-V', '--version',
                      action='store_true',
                      dest='show_version',
                      default=False,
                      help="show program's version number and exit" )

    manager = CustomCommandor(parser)
    manager.process()


if __name__ == '__main__':
    main()
