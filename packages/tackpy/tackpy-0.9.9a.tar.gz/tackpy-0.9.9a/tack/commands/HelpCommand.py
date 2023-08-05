# Authors: 
#   Trevor Perrin
#   Moxie Marlinspike
#
# See the LICENSE file for legal information regarding use of this file.

import sys
from tack.version import __version__
from tack.commands.Command import Command
from tack.commands.GenerateKeyCommand import GenerateKeyCommand
from tack.commands.SignCommand import SignCommand
from tack.commands.ViewCommand import ViewCommand
from tack.commands.PackCommand import PackCommand
from tack.commands.UnpackCommand import UnpackCommand

class HelpCommand(Command):

    COMMANDS = {"genkey" : GenerateKeyCommand, "sign" : SignCommand,
                "view" : ViewCommand, "pack" : PackCommand, "unpack" : UnpackCommand}

    def __init__(self, argv):
        Command.__init__(self, argv, "", "", allowArgRemainder=True)

        if len(self.argRemainder) < 1 or len(self.argRemainder)>1:
            HelpCommand.printGeneralUsage()

        self.command = self.argRemainder[0]

        if not self.command in HelpCommand.COMMANDS:
            self.printError("%s not a valid command." % self.command)

    def execute(self):
        HelpCommand.COMMANDS[self.command].printHelp()

    @staticmethod
    def printHelp():
        print(
"""Provides help for individual commands.

help <command>
""")

    @staticmethod
    def printGeneralUsage(message=None):
        if message:
            print ("Error: %s\n" % message)
        sys.stdout.write(
"""tack.py version %s (%s)

Commands (use "help <command>" to see optional args):
  genkey
  sign     -k KEY -c CERT
  view     FILE
  help     COMMAND
("pack" and "unpack" are advanced commands for debugging)
""" % (__version__, Command.getCryptoVersion()))
        sys.exit(-1)
