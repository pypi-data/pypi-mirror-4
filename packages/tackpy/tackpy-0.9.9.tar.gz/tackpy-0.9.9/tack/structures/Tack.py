# Authors: 
#   Trevor Perrin
#   Moxie Marlinspike
#
# See the LICENSE file for legal information regarding use of this file.

from tack.crypto.ECPublicKey import ECPublicKey
from tack.tls.TlsStructure import TlsStructure
from tack.tls.TlsStructureWriter import TlsStructureWriter
from tack.util.Util import Util
from tack.util.PEMDecoder import PEMDecoder
from tack.util.PEMEncoder import PEMEncoder
from tack.util.Time import Time

class Tack(TlsStructure):
    LENGTH =  166

    def __init__(self, data=None):
        if data is None:
            return

        TlsStructure.__init__(self, data)
        if len(data) != Tack.LENGTH:
            raise SyntaxError("Tack is the wrong size. Is %s and should be %s" % (len(data), Tack.LENGTH))        

        self.public_key     = ECPublicKey.create(self.getBytes(64))
        self.min_generation = self.getInt(1)
        self.generation     = self.getInt(1)
        self.expiration     = self.getInt(4)
        self.target_hash    = self.getBytes(32)
        self.signature      = self.getBytes(64)

        if self.generation < self.min_generation:
            raise SyntaxError("Generation less than min_generation")
            
        if not self.verifySignature():
            raise SyntaxError("Tack has bad signature")


    @classmethod
    def createFromPem(cls, pem):
        return cls(PEMDecoder(pem).decode("TACK"))

    @classmethod
    def createFromPemList(cls, data):
        """Parse a string containing a sequence of PEM Tacks.

        Raise a SyntaxError if input is malformed.
        """
        tacks = []
        bList = PEMDecoder(data).decodeList("TACK")
        for b in bList:
            tacks.append(Tack(b))

        return tacks

    @classmethod
    def create(cls, public_key, private_key, min_generation, generation, expiration, target_hash):
        assert(len(public_key.getRawKey()) == 64)
        assert(0 <= min_generation <= 255)
        assert(0 <= generation <= 255 and
               generation >= min_generation)
        assert(0 <= expiration <= 2**32-1)
        assert(len(target_hash) == 32)

        tack = cls()
        tack.public_key     = public_key
        tack.min_generation = min_generation
        tack.generation     = generation
        tack.expiration     = expiration
        tack.target_hash    = target_hash
        tack.signature      = private_key.sign(tack._getDataToSign())

        return tack

    def getTackId(self):
        return str(self.public_key)

    def serialize(self):
        return self._serializePreSig() + self.signature

    def serializeAsPem(self):
        return PEMEncoder(self.serialize()).encode("TACK")

    def verifySignature(self):
        bytesToVerify = self._getDataToSign()
        return self.public_key.verify(bytesToVerify, self.signature)

    def _getDataToSign(self):
        return bytearray("tack_sig", "ascii") + self._serializePreSig()

    def _serializePreSig(self):
        writer = TlsStructureWriter(Tack.LENGTH-64)
        writer.add(self.public_key.getRawKey(), 64)
        writer.add(self.min_generation, 1)
        writer.add(self.generation, 1)
        writer.add(self.expiration, 4)
        writer.add(self.target_hash, 32)
        return writer.getBytes()

    def __str__(self):
        """Return a readable string describing this TACK.

        Used by the "TACK view" command to display TACK objects."""
        s =\
        """key fingerprint = %s
min_generation  = %d
generation      = %d
expiration      = %s
target_hash     = %s\n""" %\
        (self.getTackId(),
         self.min_generation,
         self.generation,
         Time.posixTimeToStr(self.expiration*60),
         Util.writeBytes(self.target_hash))
        return s
