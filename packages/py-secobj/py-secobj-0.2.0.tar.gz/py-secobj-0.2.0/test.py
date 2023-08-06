#!/usr/bin/env python

from secobj import *
import unittest , os , glob

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.key = 'spam and eggs'
        self.enc = EncObject(self.key)
        self.filename = '/tmp/secobj.test'
        self.obj = [1 , 2 , 3 , 4]
        self._delFile()

    def test_file_obj_encrypt(self):
        fh = open(self.filename , 'wb')
        self.enc.encryptToFile(self.obj , fh)
        fh.close()
        fh = open(self.filename , 'rb')
        obj = self.enc.decryptFromFile(fh , True)
        self.assertEqual(self.obj , obj)
        fh.close()
        self._delFile()

    def test_filename_encrypt(self):
        self.enc.encryptToFile(self.obj , self.filename)
        obj = self.enc.decryptFromFile(self.filename , True)
        self.assertEqual(self.obj , obj)
        self._delFile()

    def test_string_encrypt(self):
        encStr , iv = self.enc.encryptToStr(self.obj)
        obj = self.enc.decryptFromStr(encStr , iv)
        self.assertEqual(self.obj , obj)
        self._delFile()

    def test_filename_chg_key(self):
        newKey = 'monkeys are awesome'
        self.enc.encryptToFile(self.obj , self.filename)
        self.enc.chgKeyForFile(self.filename , self.key , newKey)
        self.enc.updateKey(newKey)
        obj = self.enc.decryptFromFile(self.filename , True)
        self.assertEqual(self.obj , obj)
        self._delFile()

    def test_file_obj_chg_key(self):
        newKey = 'monkeys are awesome'
        fh = open(self.filename , 'w+b')
        self.enc.encryptToFile(self.obj , fh)
        fh.seek(0)
        self.enc.chgKeyForFile(fh , self.key , newKey)
        fh.seek(0)
        self.enc.updateKey(newKey)
        obj = self.enc.decryptFromFile(fh , True)
        fh.close()
        self.assertEqual(self.obj , obj)
        self._delFile()

    def tearDown(self):
        for f in glob.glob('./*.pyc'):
            try:
                os.unlink(f)
            except:
                pass
        self._delFile()

    def _delFile(self):
        try:
            os.unlink(self.filename)
        except:
            pass


if __name__ == '__main__':
    unittest.main()
