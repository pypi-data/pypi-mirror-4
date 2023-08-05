# Authors: 
#   Trevor Perrin
#   Moxie Marlinspike
#
# See the LICENSE file for legal information regarding use of this file.

import sys
from tack.commands.Command import Command
from tack.structures.TackExtension import TackExtension
from tack.tls.TlsCertificate import TlsCertificate

class UnpackCommand(Command):

    def __init__(self, argv):
        Command.__init__(self, argv, "oE", "vx")
        self.outputFile, self.outputFileName = self.getOutputFile()
        self.tackExtension = self.getTackExtension(mandatory=True)

    def execute(self):
        for tack in self.tackExtension.tacks:
            self.outputFile.write(tack.serializeAsPem())
        self.printVerbose(str(self.tackExtension))

    @staticmethod
    def printHelp():
        print(
"""Takes the input TACK Extension, and writes out PEM encodings for its Tacks.

  unpack -e EXTENSION

Optional arguments:
  -v                 : Verbose
  -o FILE            : Write the output to this file (instead of stdout)
""")
