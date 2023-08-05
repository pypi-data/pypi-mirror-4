# Authors: 
#   Trevor Perrin
#   Moxie Marlinspike
#
# See the LICENSE file for legal information regarding use of this file.

from tack.structures.Tack import Tack
from tack.tls.TlsStructure import TlsStructure
from tack.tls.TlsStructureWriter import TlsStructureWriter
from tack.util.PEMDecoder import PEMDecoder
from tack.util.PEMEncoder import PEMEncoder

class TackExtension(TlsStructure):

    def __init__(self, data=None):
        if data is None:
            return

        TlsStructure.__init__(self, data)
        self.tacks            = self._parseTacks()
        self.activation_flags = self.getInt(1)

        if self.activation_flags > 3:
            raise SyntaxError("Bad activation_flag value")

        if self.index != len(data):
            raise SyntaxError("Excess bytes in TACK_Extension")

    @classmethod
    def createFromPem(cls, data):
        return cls(PEMDecoder(data).decode("TACK EXTENSION"))

    @classmethod
    def create(cls, tacks, activation_flags):
        tackExtension                = cls()
        tackExtension.tacks          = tacks
        tackExtension.activation_flags = activation_flags

        return tackExtension

    def serialize(self):
        w = TlsStructureWriter(self._getSerializedLength())

        if self.tacks:
            w.add(len(self.tacks) * Tack.LENGTH, 2)
            for tack in self.tacks:
                w.add(tack.serialize(), Tack.LENGTH)
        else:
            w.add(0, 2)

        w.add(self.activation_flags, 1)

        return w.getBytes()

    def serializeAsPem(self):
        return PEMEncoder(self.serialize()).encode("TACK EXTENSION")

    def verifySignatures(self):
        for tack in self.tacks:
            if not tack.verifySignature():
                return False
        return True

    def _getSerializedLength(self):
        length = 0
        if self.tacks:
            length += len(self.tacks) * Tack.LENGTH

        return length + 3 # 2 byes length field, 1 byte flags

    def _parseTacks(self):
        tacksLen = self.getInt(2)
        if tacksLen:
            if tacksLen > 2 * Tack.LENGTH or tacksLen < Tack.LENGTH:
                raise SyntaxError("tacks wrong number: %d" % tacksLen)
            elif tacksLen % Tack.LENGTH != 0:
                raise SyntaxError("tacks wrong size: %d" % tacksLen)

        tacks = []
        b2 = self.getBytes(tacksLen)
        while b2:
            tacks.append(Tack(b2[:Tack.LENGTH]))
            b2 = b2[Tack.LENGTH:]
        
        return tacks

    def __str__(self):
        result = ""

        if self.tacks:
            for tack in self.tacks:
                result += str(tack)

        result += "activation_flags = %d\n" % self.activation_flags

        return result
