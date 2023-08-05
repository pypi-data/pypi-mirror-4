# Authors: 
#   Trevor Perrin
#   Moxie Marlinspike
#
# See the LICENSE file for legal information regarding use of this file.

import getpass
import sys
from tack.commands.Command import Command
from tack.crypto.ECGenerator import ECGenerator
from tack.structures.TackKeyFile import TackKeyFile

class GenerateKeyCommand(Command):

    def __init__(self, argv):
        Command.__init__(self, argv, "po", "vx")
        self.password                        = self.getPassword()
        self.outputFile, self.outputFileName = self.getOutputFile()

    def execute(self):
        password = self._getPasswordWithPrompt()
        public_key, private_key = ECGenerator.generateECKeyPair()
        keyFile  = TackKeyFile.create(public_key, private_key, password)
        self.outputFile.write(self.addPemComments(keyFile.serializeAsPem()))
        self.printVerbose(str(keyFile))

    def _getPasswordWithPrompt(self):
        if not self.password:
            password, password2 = "this", "that"
            while password != password2:
                password  = getpass.getpass("Choose password for key file: ")
                password2 = getpass.getpass("Re-enter password for key file: ")

                if password != password2:
                    sys.stderr.write("PASSWORDS DON'T MATCH!\n")

            self.password = password

        return self.password

    @staticmethod
    def printHelp():
        print(
"""Creates a new TACK key file.

  genkey

Optional arguments:
  -v                 : Verbose
  -x                 : Use python crypto (not OpenSSL)
  -o FILE            : Write the output to this file (instead of stdout)
  -p PASSWORD        : Use this TACK key password instead of prompting
""")
