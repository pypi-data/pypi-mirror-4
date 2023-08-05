#! /usr/bin/env python

# Authors: 
#   Trevor Perrin
#   Moxie Marlinspike
#
# See the LICENSE file for legal information regarding use of this file.

import sys
from tack.commands.GenerateKeyCommand import GenerateKeyCommand
from tack.commands.HelpCommand import HelpCommand
from tack.commands.SignCommand import SignCommand
from tack.commands.ViewCommand import ViewCommand
from tack.commands.PackCommand import PackCommand
from tack.commands.UnpackCommand import UnpackCommand
from tack.crypto.openssl.OpenSSL import openssl

openssl.initialize()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        HelpCommand.printGeneralUsage("Missing command")
    elif sys.argv[1] == "genkey"[:len(sys.argv[1])]:
        GenerateKeyCommand(sys.argv[2:]).execute()
    elif sys.argv[1] == "sign"[:len(sys.argv[1])]:
        SignCommand(sys.argv[2:]).execute()
    elif sys.argv[1] == "view"[:len(sys.argv[1])]:
        ViewCommand(sys.argv[2:]).execute()
    elif sys.argv[1] == "help"[:len(sys.argv[1])]:
        HelpCommand(sys.argv[2:]).execute()
    elif sys.argv[1] == "pack"[:len(sys.argv[1])]:
        PackCommand(sys.argv[2:]).execute()
    elif sys.argv[1] == "unpack"[:len(sys.argv[1])]:
        UnpackCommand(sys.argv[2:]).execute()
    else:
        HelpCommand.printGeneralUsage("Unknown command: %s" % sys.argv[1])
