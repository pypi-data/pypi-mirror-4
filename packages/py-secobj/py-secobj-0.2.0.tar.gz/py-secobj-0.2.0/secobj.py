"""
This module will allow you to encrypt/decrypt an object to disk or 
to a string.  This will allow you to, using a passphrase, safely store
or transmit python objects.  The only non-standard library necessity
is the PyCrypto library available via a package manager or at:

    https://www.dlitz.net/software/pycrypto/

import secobj

passphrase = 'spam and eggs'
fname = '/var/tmp/test.enc'
myObj = [1 , 2 , 3]
enc = secobj.EncObject(passphrase)
    
# Encrypt to file and decrypt
enc.encryptToFile(myObj , fname)
unencryptedObject = enc.decryptFromFile(fname , True)
       
# Encrypt to string.  You will need to hold on to your IV here
encStr , IV = enc.encryptToStr(myObj)
unencryptedObject  = enc.decryptFromStr(encStr , IV)
"""

# Copyright (C) 2013  Jay Deiman
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import Crypto.Random as crandom
from hashlib import sha256
from Crypto.Cipher import AES
from cStringIO import StringIO
import cPickle as pickle
import os , struct

class DecryptError(Exception):
    pass

class EncObject(object):
    def __init__(self , key):
        """
        Initialize the encryptor/decryptor.

        key:str     The passphrase used to encrypt/decrypt
        """
        # Hash the key as we will use the hash instead of the actual
        # key for encryption/decryption
        self._hkey = ''
        self.updateKey(key)
        self._pckFmt = '!I'
        self._blkSize = AES.block_size

    def updateKey(self , newKey):
        """
        Change the key value used for encrypt/decrypt and return the new
        digest

        newKey:str      The new passphrase

        returns:str    
        """
        s = sha256()
        s.update(newKey)
        self._hkey = s.digest()
        return self._hkey

    @classmethod
    def chgKeyForFile(cls , fobj , curKey , newKey):
        """
        Changes the key for a previously encrypted object.  Note that 
        this is a class method.

        fobj:(str|file)     A string filename to write the object to
                            or a file-like object.  Note that the
                            object will be written wherever the
                            current position is if it is a file-like
                            object.
        curKey:str          The passphrase used to encrypt the file 
                            originally
        newKey:str          The new passphrase to use when encrypting the
                            file again
        """
        fh = fobj
        closeFile = False
        if isinstance(fh , basestring):
            # We have a filename
            closeFile = True
            fh = open(fobj , 'r+b')
        inst = cls(curKey)
        # Decrypt the object
        fh.seek(0)
        obj = inst.decryptFromFile(fh)
        # Truncate the file
        fh.seek(0)
        fh.truncate()
        # Update the key and reencrypt
        inst.updateKey(newKey)
        inst.encryptToFile(obj , fh)
        # Close the file, if necessary
        if closeFile:
            fh.close()

    def encryptToFile(self , obj , fobj):
        """
        Encrypt the object and store it on disk.

        obj:object          The object to encrypt.  The must be 
                            "pickleable"
        fobj:(str|file)     A string filename to write the object to
                            or a file-like object.  Note that the
                            object will be written wherever the
                            current position is if it is a file-like
                            object.
        """
        fh = fobj
        closeFile = False
        if isinstance(fh , basestring):
            # We have a filename
            closeFile = True
            fh = open(fobj , 'wb')
        # Get a stringIO object and the data length
        sio = self._getStrIOObj(obj , False)
        dLen = sio.tell()
        sio.seek(0)
        iv = self._genIV()
        aes = AES.new(self._hkey , AES.MODE_CBC , iv)
        fh.write(iv)
        # The first block is the length plus the first 12 bytes
        buf = '%s%s' % (struct.pack(self._pckFmt , dLen) , sio.read(12))
        while len(buf):
            fh.write(aes.encrypt(buf))
            buf = sio.read(self._blkSize)
        if closeFile:
            # Only close a file opened in this method
            fh.close()
        sio.close()

    def decryptFromFile(self , fobj , delFile=False):
        """
        Decrypts and returns object from disk

        fobj:(str|file)     A string filename or file-like object to
                            read from.  Note that the object will be
                            read from whereever the current file
                            position is if it is a file-like object.
        delFile:bool        Remove the file after decrypting its contents.
                            This will raise an IOError if the file can't
                            be deleted for some reason.

        returns:object
        """
        fh = fobj
        closeFile = False
        if isinstance(fh , basestring):
            closeFile = True
            fh = open(fobj , 'rb')
        fname = fh.name
        # Read in the IV
        iv = fh.read(self._blkSize)
        aes = AES.new(self._hkey , AES.MODE_CBC , iv)
        buf = aes.decrypt(fh.read())
        rawLen = len(buf[4:])
        buf = buf.rstrip('\x00')
        if closeFile:
            # Only close a file opened in this method
            fh.close()
        if delFile:
            os.unlink(fname)
        # The first 4 bytes will be the packed int length
        dLen = struct.unpack(self._pckFmt , buf[:4])[0]
        if dLen != rawLen:
            raise DecryptError('Invalid data length. This is usually a '
                'bad passphrase. Expected len: %d; Actual len: %d' %
                (dLen , rawLen))
        # Return the unpickled object
        try:
            obj = pickle.loads(buf[4:])
        except:
            raise DecryptError('Error decrypting and loading the object. '
                'Likely this is an invalid passphrase or IV')
        return obj

    def encryptToStr(self , obj):
        """
        Encrypts an object to a string and returns the string and 
        the IV used in the process.  Unlike encryptToFile, the data
        length will *not* be encrypted as part of the blob, it will 
        only be the object itself (with null byte padding at the end).

        obj:object      The object to encrypt

        returns(str:encObj , str:IV)
        """
        iv = self._genIV()
        sio = self._getStrIOObj(obj)
        aes = AES.new(self._hkey , AES.MODE_CBC , iv)
        enc = aes.encrypt(sio.getvalue())
        sio.close()
        return (enc , iv)

    def decryptFromStr(self , encStr , iv):
        """
        Decrypts an object from a string encrypted with encryptToStr
        and returns it

        encStr:str      The encrypted object string
        iv:str          The IV used to encrypt the object

        returns:object
        """
        aes = AES.new(self._hkey , AES.MODE_CBC , iv)
        buf = aes.decrypt(encStr).rstrip('\x00')
        try:
            obj = pickle.loads(buf)
        except:
            raise DecryptError('Error decrypting and loading the object. '
                'Likely this is an invalid passphrase or IV')
        return obj
        
    def _genIV(self):
        """
        Returns an IV
        """
        return crandom.get_random_bytes(self._blkSize)
        
    def _getStrIOObj(self , obj , padFull=True):
        """
        Pickles the object and pads it will null bytes

        obj:object      The object to be stringified
        padFull:bool    If this is False, it will pad at block
                        size minus four to account for the 
                        unsigned int pre-pended in file encryption.
                        Otherwise, it will be padded to block size.

        returns:StringIO
        """
        sio = StringIO()
        sio.write(pickle.dumps(obj))
        dataLen = sio.tell()
        # Subtract 4 for the unsigned int length that's prepended
        subSize = self._blkSize
        if not padFull:
            subSize -= 4
        pad = subSize - dataLen % self._blkSize
        if pad != self._blkSize:
            sio.write('\x00' * pad)
        return sio
